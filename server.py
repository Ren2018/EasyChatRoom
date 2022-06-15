import socket,io,time,struct,os
import cv2
from PIL import Image,ImageGrab
from threading import Thread

host = '127.0.0.1'
port = 8080

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind((host,port))

client = {}
address = {}
accept_num = 10

def get_picture():
    capture = cv2.VideoCapture(0)
    ret,frame = capture.read()
    cv2.imwrite("temp.jpg",frame)
    capture.release()
    cv2.destroyAllWindows()

def get_cut():
    #ig = ImageGrab.grab((760,0,1160,1080))
    ig = ImageGrab.grab()
    ig.save('cut.jpg')

def set_image(fileName):
    im = Image.open(fileName)
    bytesIo = io.BytesIO()
    try:
        im.save(bytesIo, format = 'JPG')
    except:
        im.save(bytesIo, format = 'PNG')
    return bytesIo.getvalue()

def send_image(imagfile):
    print("imageByte"+imagfile)
    for con in client:
        con.send(bytes("传输文件\n",'utf-8'))
        fileinfo_size = struct.calcsize('128sl')
        fhead = struct.pack('128sl',bytes(os.path.basename(imagfile).encode('utf-8')),os.stat(imagfile).st_size)
        con.send(fhead)
        try:
            with open(imagfile, 'rb') as f:
                while True:
                    print("传输文件")
                    f_data = f.read(1024)
                    if f_data:
                        con.send(f_data)
                    else:
                        break
                f.flush()
                f.close()
            #con.send(bytes("\n", 'utf-8'))
            print("传输文件结束")
        except Exception as e:
            print(e)


def brodcast(msg,addr,nikename = ''):
    for con in client:
        print("---addr"+str(addr[con][1]))
        print("---conn" + str(con))
        con.send(bytes(nikename,'utf-8')+msg)


def handle_client_in(conn,addr):
    nikename = conn.recv(1024).decode('utf-8')
    nikename = nikename.strip('\n')
    welcome = f'{nikename} 加入聊天室\n'
    client[conn] = nikename
    brodcast(bytes(welcome,'utf-8'),addr)
    while True:
        try:
            msg = conn.recv(1024)
            if msg.decode('utf-8').strip().strip('\n') == "拍照":
                get_picture()
                send_image("temp.jpg")
            elif msg.decode('utf-8').strip().strip('\n') == "截屏":
                print("截屏")
                get_cut()
                #imageByte = set_image("cut.jpg")
                send_image("cut.jpg")
            else:
                brodcast(msg,addr,nikename+':')
        except Exception as e:
            print(e)
            #conn.close()
            #client.pop(conn)
            #if client[conn]:
            del client[conn]
            brodcast(bytes(f'{nikename} 离开了聊天室\n', 'utf-8'),addr)


if __name__ == '__main__':
    s.listen(accept_num)
    print('服务器已经启动，正在监听客户端请求...')
    while True:
        conn , addr = s.accept()
        print(addr,'已经建立连接')
        conn.send('欢迎来到聊天室\n'.encode('utf-8'))
        #conn.send('请输入您的聊天昵称\n'.encode('utf-8'))
        address[conn] = addr
        Thread(target=handle_client_in,args=(conn,address)).start()


