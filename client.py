from tkinter import Tk,Frame,Text,Button,Label,Canvas,messagebox
from tkinter.ttk import Combobox
from tkinter.constants import INSERT,W,E,N
from PIL import Image,ImageTk,ImageFile
import socket,struct,os
import cv2
from threading import Thread

Host = '127.0.0.1'
SendPort = 8080

root = Tk()
root.title('简易聊天室')

def send_msg():
    print('触发发送事件')
    send_msg = text_text.get('0.0','end')
    print(send_msg)
    soc.send(bytes(send_msg,'utf-8'))
    text_text.delete('0.0','end')

def conntion():
    address = combobox.get().split(":")
    print(address)
    try:
        soc.connect((address[0], int(address[1])))
        localip = soc.getsockname()[0]
        soc.send(bytes(("IP:" + localip), 'utf-8'))
        receive_thread = Thread(target=get_msg)
        receive_thread.start()
        messagebox.showinfo('提示', '连接成功')
    except Exception as e:
        print(e)
        messagebox.showinfo('提示', '连接失败，请检查目标节点')

def picture():
    soc.send(bytes("拍照\n",'utf-8'))

def cut():
    soc.send(bytes("截屏\n",'utf-8'))

def quit_tk():
    soc.close()
    root.quit()

#ImageFile.LOAD_TRUNCATED_IMAGES=True
option_frame = Frame(width=480,height=400)
message_frame = Frame(width=480,height=100,bg='white')
text_frame = Frame(width=480,height=80)
send_frame = Frame(width=480,height=30)

values = [1, 2, "127.0.0.1:8080", 4, 5, "Text"]
target = Label(option_frame,text='节点')
combobox = Combobox(option_frame,text='列表',values = values)
button_conntion = Button(option_frame,text='连接',command=conntion,fg = "green")
button_picture = Button(option_frame,text='拍照',command=picture,fg = "green")
button_cut = Button(option_frame,text='截屏',command=cut,fg = "green")
#label_image = Label(option_frame, width = 80, height=30, bg = "white")
canvas_image = Canvas(option_frame, width = 300, height=300, bg = "white")
text_message = Text(message_frame)
text_text = Text(text_frame)
button_send = Button(send_frame,text='发送',command=send_msg,fg = "green")
button_quit = Button(send_frame,text='退出',command=quit_tk,fg = "red")

target.grid(row=0,column=0,padx = 10)
combobox.grid(row=0,column=1)
button_conntion.grid(row=0,column=2,padx = 10)
button_picture.grid(row=1,column=1)
button_cut.grid(row=2,column=1)
#label_image.grid(row=0, column=4, rowspan=3)
canvas_image.grid(row=0, column=4, rowspan=3)
button_send.grid(row=0,column=0,sticky = W)
button_quit.grid(row=0,column=1,sticky = E,padx = 410)

option_frame.grid(row=0,column=0)
message_frame.grid(row=1,column=0,padx=3,pady=6)
text_frame.grid(row=2,column=0,padx=3,pady=6)
send_frame.grid(row=3,column=0)

message_frame.grid_propagate(0)
text_frame.grid_propagate(0)
send_frame.grid_propagate(0)

text_message.grid()
text_text.grid()
#button_send.grid()

def get_msg():
    while True:
        try:
            byt = soc.recv(1024)
            msg = byt.decode('utf-8')
            text_message.configure(state='normal')
            #text_message.insert('end',msg)
            #print(byt)
            if msg.strip().strip('\n') == "传输文件":
                fileinfo_size = struct.calcsize('128sl')
                buf = soc.recv(fileinfo_size)
                filename, filesize = struct.unpack('128sl',buf)
                fn = filename.strip(str.encode('\00'))
                new_filename = os.path.join(str.encode('./'),str.encode('new_')+fn)
                recvd_size = 0
                with open(new_filename,'wb') as f:
                    while not recvd_size == filesize:
                        print("接收文件")
                        if filesize - recvd_size > 1024:
                            f_data = soc.recv(1024)
                            recvd_size += len(f_data)
                        else:
                            f_data = soc.recv(filesize - recvd_size)
                            recvd_size = filesize
                        f.write(f_data)
                    f.close()
                print("传输接收结束")
                img = Image.open(new_filename).resize((300, 300), Image.ANTIALIAS)
                im = ImageTk.PhotoImage(img)
                #label_image.configure(image=im)
                #label_image.image = im
                canvas_image.create_image(150,150,image = im) # 前面两个偏移量为图片大小的一半
            elif msg.split(':')[0] == 'Ren':
                my_button = Button(text_message, text=msg)
                text_message.window_create(INSERT,window=my_button)
            else:
                text_message.insert('end', msg)
            text_message.configure(state='disabled')
        except:
            break


if __name__ == '__main__':
    #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #s.connect((Host, SendPort))
    #localip = socket.gethostbyname(socket.gethostname())
    #localip = s.getsockname()[0]
    #s.send(bytes(("IP:"+localip),'utf-8'))
    #receive_thread = Thread(target=get_msg)
    #receive_thread.start()
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    root.mainloop()
