text = "WRAP.THE.FOLLOWING.TEXT.INTO.SCC.FLAG.FORMAT.BANEOFARTHROPODSV"
for i in text:
    print('\\includegraphics{"./assets/char(' + str(ord(i)) + ').png"}')
