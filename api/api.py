import os
import pathlib
from pykml import parser
from flask import Flask, jsonify, flash, request, redirect, url_for
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
from flask import send_from_directory
import zipfile
import glob
import shutil

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'mysql'
app.config['MYSQL_USER'] = 'pila'
app.config['MYSQL_PASSWORD'] = 'pila'
app.config['MYSQL_DB'] = 'pila'
mysql = MySQL(app)

UPLOAD_FOLDER = '/app/maps'
ALLOWED_EXTENSIONS = {'kmz'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 128 * 1000 * 1000
app.add_url_rule(
    "/uploads/<name>", endpoint="download_file", build_only=True
)
app.add_url_rule(
    "/success/<name>", endpoint="success_file_upload", build_only=True
)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def fast_scandir(dirname):
    subfolders= [f.path for f in os.scandir(dirname) if f.is_dir()]
    for dirname in list(subfolders):
        subfolders.extend(fast_scandir(dirname))
    return subfolders


@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/locations', methods=['GET'])
def locations():
    cur = mysql.connection.cursor()
    cur.execute('''
        select UNIX_TIMESTAMP(l.date) as date, l.id, l.type, l.lat, l.lng
        from locations l, (select max(date) as d, id FROM locations where lat > 0 and lng > 0 group by id) lg 
        where lg.id = l.id and lg.d = l.date
    ''')
    data = cur.fetchall()
    cur.close()
    response = jsonify(data)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            extension = filename[-3:]
            extdir = os.path.join(app.config['UPLOAD_FOLDER'], extension)
            if not os.path.exists(extdir):
                os.makedirs(extdir)
            filepath = os.path.join(extdir, filename)
            file.save(filepath)

            unzipfolder = filepath[:-4]

            with zipfile.ZipFile(filepath, 'r') as zip_ref:
                zip_ref.extractall(unzipfolder)

            #remove original kmz file
            if extension == 'kmz':
                if os.path.exists(filepath):
                    os.remove(filepath)

            return redirect(url_for('success_file_upload', name=filename))
    return '''
    <!doctype html>
    <title>Загрузка карт в формате KMZ</title>
    <h1>Загрузка карт в формате KMZ</h1>
    <h2>KMZ файл содержит внутри файлы: doc.kml и jpg фрагменты карт</h2>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Загрузить>
    </form>
    <p/>
    <p/>
    <form method=post action="/removeall">
      <input type=submit value="Удалить все карты">
    </form>
    '''

@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

@app.route('/success/<name>')
def success_file_upload(name):
    return '''
    <!doctype html>
    <title>Файл успешно загружен</title>
    <h1>Файл успешно загружен</h1>
    <h1>''' + name + '''</h1>
    <a href='/upload'>Вернуться к загрузке карт</a>
    '''

@app.route('/removeall', methods=['POST'])
def remove_all():
    files = glob.glob(os.path.join(app.config['UPLOAD_FOLDER'], '*'))
    for f in files:
        if os.path.isfile(f) or os.path.islink(f):
            os.remove(f)  # remove the file
        elif os.path.isdir(f):
            shutil.rmtree(f)  # remove dir and all contains


    return '''
    <!doctype html>
    <title>Удаление файлов</title>
    <h1>Все файлы и папки с картами успешно удалены</h1>
    <a href='/upload'>Вернуться к загрузке карт</a>
    '''

@app.route('/localmaps', methods=['GET'])
def localmaps():
    kmzfolder = os.path.join(app.config['UPLOAD_FOLDER'], 'kmz')
    mapjsons = {}
    if os.path.exists(kmzfolder):
        subfolders = fast_scandir(kmzfolder)
        mapjsons = getAllKmzLocalMaps(subfolders)
    response = jsonify(mapjsons)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

def getAllKmzLocalMaps(dirname):
    mapjsons = []
    for folder in dirname:
        path = pathlib.PurePath(folder)
        mapname = path.name
        mapjson = {
            "name": mapname
        }
        #print(mapjson)
        dockmlpath = folder + "/doc.kml"
        #print(dockmlpath)

        with open(dockmlpath, 'r', encoding="UTF-8") as f:
            root = parser.parse(f).getroot()

        images = []
        for image in root.Document.GroundOverlay:
            data = {}
            data["file"] = image.Icon.href.text.strip()
            north = image.LatLonBox.north.text.strip()
            south = image.LatLonBox.south.text.strip()
            east = image.LatLonBox.east.text.strip()
            west = image.LatLonBox.west.text.strip()
            data["north"] = north
            data["south"] = south
            data["east"] = east
            data["west"] = west
            images.append(data)
        mapjson["data"] = images
        mapjsons.append(mapjson)

    return mapjsons



if __name__ == '__main__':
    app.run(debug=True)
    