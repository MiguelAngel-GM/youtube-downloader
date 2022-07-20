from pytube import YouTube, Playlist
import os
import subprocess


again = True


def downloadAudio(url, path='', list_mode=False):
    if not list_mode:
        try:
            yt = YouTube(url)
        except:
            print("El enlace introducido es erroneo")
            repeat()
            return
    else: yt = url

    print("Un momento...")
    audio_stream = yt.streams.get_audio_only()
    size = "{:.2f}".format(float(audio_stream.filesize)/1048576)
    print(f"Va a descargarse el archivo {yt.title}.mp3 ({size} mb)")
    
    if not list_mode:
        path = input("En que ruta quieres guardar tu descarga? (Si se deja en blanco, la descarga se guardara en el directorio donde se encuente ubicado el programa)\n> ")
        if (path != '' and path[-1] != '/'): path += '/'

    try:
        print("Descargando el archivo...")
        file = path + yt.title + '.mp4'
        audio_stream.download(output_path=path, filename=file)
        file_mp3 = path + yt.title +'.mp3'
        print("Realizando conversion a mp3...")
        subprocess.run(["ffmpeg", "-i", file, "-vn", file_mp3])    #el archivo descargado se convierte a mp3 (pytube descarga en mp4)
        os.remove(file)
    except:
        print("Error en la descarga, revisa que los parametros sean correctos y que tienes conexion a internet.\n\n")
        repeat()
        return

    if not list_mode:
        repeat()



def downloadVideo(url, path='', res='', list_mode=False):
    if not list_mode:
        try:
            yt = YouTube(url)
        except:
            print("El enlace introducido es erroneo")
            repeat()
            return
    else: yt = url

    print("Un momento...")
    video_streams = yt.streams.filter(progressive=True)   #lista de streams de video y audio (restringido a 720p)
    
    if not list_mode:
        res = [stream.resolution for stream in video_streams]
        print(f"Las resoluciones disponibles son {res}")
        res = input("Elige resolucion entre las disponibles\n> ")
        path = input("En que ruta quieres guardar tu descarga? (Si se deja en blanco, la descarga se guardara en el directorio donde se encuente ubicado el programa)\n> ")
        if (path != '' and path[-1] != '/'): path += '/'

    try:
        size = "{:.2f}".format(float(video_streams.get_by_resolution(str(res)).filesize)/1048576)
        print(f"Va a descargarse el archivo {yt.title}.mp4 ({size} mb)")
        video_streams.get_by_resolution(str(res)).download(output_path=path)
    except:
        print("No puede descargarse el video a la resolucion introducida, se va a descargar a la resolucion mas alta disponible")
        size = "{:.2f}".format(float(video_streams.get_highest_resolution().filesize)/1048576)
        print(f"Va a descargarse el archivo {yt.title}.mp4 ({size} mb)")
        video_streams.get_highest_resolution().download(output_path=path)

    if not list_mode:
        repeat()



def handleList(url, mode):
    try:    
        pl = Playlist(url)
        print(f"Va a descargarse la lista {pl.title}")
    except:
        print("El enlace introducido es erroneo")
        repeat()
        return

    list_path = input("En que ruta quieres guardar tu descarga? (Si se deja en blanco, la descarga se guardara en el directorio donde se encuente ubicado el programa)\n> ")
    if (list_path != '' and list_path[-1] != '/'): list_path += '/'

    if mode.lower() == 'audio':
        for video in pl.videos:
            downloadAudio(video, list_path, list_mode=True)
    elif mode.lower() == 'video':
        list_res = input("A que resolucion quieres descargar los videos de la lista? (720p max)\n> ")
        for video in pl.videos:
            downloadVideo(video, list_path, list_res, list_mode=True)

    repeat()



def repeat():
    global again
    os.system("clear")
    print("Hecho!")

    while True:
        op = input("Quieres hacer algo mas? (S/N) --> ")
        
        if op.lower() == 's':
            again = True
            break
        elif op.lower() == 'n':
            again = False
            print("Adios :)")
            break
        else:
            print("Opcion invalida, solo son validas las opciones si y no, prueba otra vez")



def main():
    print("Hola :)")
    global again

    while again == True:
        option = input("Quieres descargar un video o una lista?\n> ")
        
        if option.lower() == 'video':
            url = input("Introduce el enlace al video que quieres descargar\n> ")
            mode = input("Quieres descargar el video completo o solo audio? (Escribe audio o video)\n> ")

            if mode.lower() == 'audio': downloadAudio(url)
            elif mode.lower() == 'video': downloadVideo(url)
            else: print("Opcion invalida, solo son validas las opciones video y audio, prueba otra vez")

        
        elif option.lower() == 'lista':
            url = input("Introduce el enlace a la lista que quieres descargar\n> ")
            mode = input("Quieres descargar los videos completos o solo su audio? (Escribe audio o video)\n> ")

            if mode.lower() not in ['audio', 'video']: print("Opcion invalida, solo son validas las opciones video y audio, prueba otra vez")        
            else: handleList(url, mode)

        else:
            print("Opcion invalida, solo son validas las opciones video o lista. Intentalo de nuevo")





if __name__ == "__main__":
    main()
