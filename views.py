# In views.py 
#Requests ---> from pydub import AudioSegment
# The convertor voice recognition can work together with another convertor (audio convertor)
@login_required() # an user can only convert a file if is logged in 
def fileupload(request): #upload file function plus call the convert program and generates the txt file
    if request.method == 'POST':
        form = FileInfoForm(request.POST, request.FILES)
        if form.is_valid():
            fileinfo = form.save(commit=False)
            fileinfo.user = request.user

            name, ext = os.path.splitext(request.FILES['audio_file'].name) #audio-text convertor
            # import pdb
            # pdb.set_trace()
            if ext == '.mp3': # if clause that calls audio convertor
                with tempfile.NamedTemporaryFile(delete=False) as tf: #audio-text convertor
                    tf.write(request.FILES['audio_file'].read()) #audio-text convertor
                    tf.seek(0) #audio convertor
                    sound = AudioSegment.from_mp3(tf.name)#audio convertor
                    # path = os.path.join(settings.MEDIA_ROOT, 'audios', '{}.wav'.format(name))

                    with tempfile.NamedTemporaryFile(delete=False) as wavfile: #audio text-convertor
                        sound.export(wavfile.name, format="wav")
                        fileinfo.audio_file = FileSystemStorage().save(     #audio text-convertor
                            'audios/%s.wav' % splitext(basename(fileinfo.audio_file.name))[0], wavfile)
                file = BytesIO(fileinfo.audio_file.read())

            else:
                file = BytesIO(request.FILES['audio_file'].read())
            # getting the converted text
            text_converted = convert_audio(file)
            # saving the converted text in memory
            with StringIO() as t:
                t.write(text_converted)
                # setting the text_file with the text in memory saved before
                fileinfo.text_file = FileSystemStorage().save(
                    'texts/%s.txt' % splitext(basename(fileinfo.audio_file.name))[0], t)
                fileinfo.text_data = text_converted
            fileinfo.save()
            return redirect(reverse('filelist'))

    else:
        form = FileInfoForm()
    return render(request, 'polls/upload.html', {'form': form})


import datetime   
@login_required()
def filedownload(request, pk): #gives the option to download the txt file
    fileinfo = get_object_or_404(FileInfo, pk=pk, user=request.user)
    response = HttpResponse(fileinfo.text_file.read(), content_type='application/text')
    response['Content-Disposition'] = 'attachment; filename=' + basename(fileinfo.text_file.name)
    return response
