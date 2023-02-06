from pytube import YouTube, Playlist, exceptions
import os
import subprocess
import argparse
import concurrent.futures

def createParser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(epilog="Unless specified via the -v flag, the videos will be downloaded as an audio only stream and converted to mp3")
    parser.add_argument("url", help="URL for the video/playlist")
    parser.add_argument("path", help="Output file path. If left empty the output will be saved in the current directory", default="", nargs="?")
    parser.add_argument("-p", "--playlist", help="indicates that the URL corresponds to a YouTube playlist", action="store_true")
    parser.add_argument("-v", "--video", help="download video in a specified resolution and save it as an mp4 file", action="store_true")
    parser.add_argument("-r", "--res", help="resolution for the video in case -v is active", 
                        choices=["144p", "240p", "360p", "480p", "720p"], default="360p", const="360p", nargs="?")
    return parser
    

def downloadAudio(url, path, is_playlist=False):
    if not is_playlist:
        try:
            yt = YouTube(url)
        except exceptions.PytubeError as e:
            print(f"[ERROR] Pytube raised an exception with the following error message: {e.args[0]}")
            return -1
        if (path != '' and path[-1] != '/'): path += '/'
    else: yt = url

    try:
        print(f"Getting audio streams for {yt.title}...")
        audio_stream = yt.streams.get_audio_only()
        size = "{:.2f}".format(float(audio_stream.filesize)/2**20)
        print(f"Downloading {yt.title}.mp4 ({size} mb)...")

        title = ''.join(char for char in yt.title if char.isalnum() or char.isspace())  # this avoids problems when calling ffmpeg

        file = path + title + '.mp4'
        audio_stream.download(output_path=path, filename=file)
        file_mp3 = path + title + '.mp3'
        print("Converting to mp3...")
        subprocess.run(["ffmpeg", "-i", file, "-vn", file_mp3, "-loglevel", "quiet"])    # ffmpeg command to convert to mp3
        os.remove(file)
    except KeyError:
        print(f"[ERROR] Couldn't get stream data")
        return -1
    except exceptions.PytubeError as e:
        print(f"[ERROR] Pytube raised an exception with the following error message: {e.args[0]}")
        return -1

    print("Done!")



def downloadVideo(url, path, res, is_playlist=False):
    if not is_playlist:
        try:
            yt = YouTube(url)
        except exceptions.PytubeError as e:
            print(f"[ERROR] Pytube raised an exception with the following error message: {e.args[0]}")
            return -1
        if (path != '' and path[-1] != '/'): path += '/'
    else: yt = url
        
    try: 
        print(f"Getting video streams for {yt.title}...")
        video_streams = yt.streams.filter(progressive=True)   # video and audio stream list (restricted to 720p)
        
        video = video_streams.get_by_resolution(res)
        if video == None:
            print("[WARNING] Couldn't download video with the requested resolution, the video will be downloaded at the highest resolution available.")
            video = video_streams.get_highest_resolution()
        
        size = "{:.2f}".format(float(video.filesize)/2**20)
        print(f"Downloading {yt.title}.mp4 ({size} mb)...")
        video.download(output_path=path)
    except KeyError:
        print(f"[ERROR] Couldn't get stream data")
        return -1
    except exceptions.PytubeError as e: 
        print(f"[ERROR] Pytube raised an exception with the following error message: {e.args[0]}")
        return -1
    
    print("Done!")


        

def handleList(url, path, res, mode):
    try:    
        pl = Playlist(url)
        print(f"Downloading playlist: {pl.title}")
    except exceptions.PytubeError as e:
        print(f"[ERROR] Pytube raised an exception with the following error message: {e.args[0]}")
        return -1

    if (path != '' and path[-1] != '/'): path += '/'

    with concurrent.futures.ThreadPoolExecutor() as executor:
        if mode == 0:
            for video in pl.videos:
                executor.submit(downloadAudio, video, path, True)
        else:
            for video in pl.videos:
                executor.submit(downloadVideo, video, path, res, True)


def processArguments(args):
    if args.video:
        if args.playlist:
            handleList(args.url, args.path, args.res, 1)
        else:
            downloadVideo(args.url, args.path, args.res)
    else:
        if args.playlist:
            handleList(args.url, args.path, args.res, 0)
            os.system("reset")
        else:
            downloadAudio(args.url, args.path)



def main():
    parser = createParser()
    args = parser.parse_args()

    processArguments(args)

    
if __name__ == "__main__":
    main()
