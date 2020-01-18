import cv2
from time import sleep
import numpy
from datetime import datetime
import serial
import picamera
import shutil
from os import system

  
ser = serial.Serial('/dev/ttyACM0', 9600) #Arduino Baglanti (USB)

def initialize_Serial(): #Arduino ilk deger atama
    sleep(1)
    ser.write(b'-1') #Sifir Degeri Ata
    sleep(1)

def write_Serial(pwm_value): # Arduino'ya pwm degeri yolla
    sleep(1)
    ser.write(pwm_value.encode()) #PWM degerini binary olarak kodla ve yolla
    sleep(1)

def calculate_mean(): #Kameradan Degerleri al 
    with picamera.PiCamera() as camera: # Kamerayi tanimla
        stream = open('image.data', 'w+b') #gorsel icin degisken hazirla
        camera.framerate = 5 # kamera fps'i
        sleep(2) 
        camera.shutter_speed = 36850 #Kamera Cekme Hizi (mikrosaniye)
        camera.exposure_mode = 'off' #Otomatik duzeltme kapatma
        g = camera.awb_gains #Otomatik beyazlatma orani
        camera.iso = 100 # ISO
        camera.awb_mode = 'off' #Otomatik beyazlatma Kapali
        camera.awb_gains = g #Beyazlatma Oranini ata
        width = 1280 #Goruntu Boyutlari
        height = 720
        camera.resolution = (width, height) #Kamera Cozunurlugu 
        camera.start_preview() #Goruntu Baslat
        sleep(2)
        camera.capture(stream, 'yuv') # Resmi Al
        stream.seek(0)
        fwidth = (width + 31) // 32 * 32 # Resim Boyutlarini Ayarla
        fheight = (height + 15) // 16 * 16
        # Y kanalini (isiklandirma) cikart
        Y = numpy.fromfile(stream, dtype=numpy.uint8, count=fwidth*fheight).\
        reshape((fheight, fwidth))
        return (numpy.average((numpy.average(Y, axis=0)))) # Iki boyutlu Y Kanalinin Ortalama Degerini Cikart

def calculate_Lux(avg): # Toplam Isik Degerini Hesapla
    print("Ic Isiklar Acik")
    #print(avg)    
    B = 81.3161669250621 # Toplam Isik Sabiti
    Err = 0.194858452777609      # Toplam Isik Hata Orani
    return abs((avg-B)/Err)

def get_frames():    
    return calculate_mean()

def calculate_outer_lux(avg): # Dis isik Degerini Hesapla
    print("Ic Isiklar Kapali")
    #print(avg)
    if avg < 30: # Dis isik dusukse Hesaplamadan cik
        return 0
    B = 62.7637685159081 # Dis isik sabiti
    Err = 0.503275917659405 # Dis isik hata orani
    return abs((avg-B)/Err)

pwm_const = 2.73
def pwm_to_lux(pwm_value): #PWM ile toplam isik degerini hesapla
    print("pwm degeri : ", pwm_value)
     #PWM sabiti
    return pwm_value*pwm_const 
             
def measure_outer():
    outer_lux = calculate_outer_lux(calculate_mean()) #Dis isik degerini hesapla
    print("Dis Isik Degeri : ",outer_lux)  
    return outer_lux   
    
def measure_light(pwm=0, outer_lux=0):  
    if pwm != 0 :            
        total_lux = calculate_Lux(get_frames()) #Toplam Isik Degerini Hesapla
        pwm_lux = pwm_to_lux(pwm)+outer_lux #PWM ile isik siddetini hesapla
        avg_lux = (pwm_lux+total_lux)/2
        print("Isik Siddeti PWM Olcumu:", (pwm_lux))
        print("Isik Siddeti :", (total_lux))        
        print("Isik Siddeti Ortalama Deger : ", (avg_lux)) # Hata orani hesaplanmis toplam isik degerini hesapla
        return avg_lux

zero = [0,0,0]  
def arrange_pwm(lux):        
    pwm = 0
    if zero[0]==0:        
        outer_lux = measure_outer()        
        pwm = lux_to_pwm(lux, outer_lux)
        zero[1] = outer_lux
    else:
        inner_lux = measure_light(zero[0], zero[1])        
        pwm = lux_to_pwm(lux, zero[1])
        zero[2] = inner_lux
    write_Serial(str(pwm))
    zero[0] = pwm
    system('clear')
    print(zero[1])
    measure_light(pwm, zero[1])
    
def lux_to_pwm(lux_to_reach, existing_lux):
    
    return int(abs(lux_to_reach - existing_lux)/pwm_const)

def stream_live():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        cv2.imshow('frame', frame)
        if cv2.waitKey(10) == ord('q'): #   Kapatma Komutunu Bekle
            break
    cap.release()
    cv2.destroyAllWindows()
    
columns = shutil.get_terminal_size().columns        
def default_menu():
    initialize_Serial()
    while True:
        system('clear')
        print("Hosgeldiniz".center(columns))
        print("Yapmak Istediginiz Islemi Lutfen Asagidan Seciniz :")
        print("\t1 - Ortam Isik Degerini Hesapla")
        print("\t2 - Istenilen Isik Degerini Ayarla")
        print("\t3 - Depo Isigi")
        print("\t4 - Ofis Isigi")
        print("\t5 - Hastane Muayene Odasi Isigi")
        print("\t6 - Yuzey Hazirlama ve Boyama Isigi" )
        print("\t8 - Dis Isik Degeri Degisti" )
        print("\t9 - Canli Yayin Yap")
        print("\t0 - Cikis")
        
        print('Seciminizi Giriniz :', end = ' ')
        res = get_choise(input())
        
        if res == -1 :
            return
def get_choise(choise):
    
    if choise == "1":
        if zero[0] == 0:
            measure_outer()
        else:
            measure_light(zero[0], zero[1])
    elif choise == "2":
        print("\tLutfen Istediginiz Isik Degerini Giriniz :", end = ' ')
        Lux = int(input())
        arrange_pwm(Lux)
    elif choise == "3":
        arrange_pwm(100)
    elif choise == "4" or choise == "5":
        arrange_pwm(500)
    elif choise == "6":
        arrange_pwm(750)
    elif choise == "8":
        initialize_Serial()
        zero[0] = 0
        arrange_pwm(50)
    elif choise == "9":
        stream_live()
    elif choise == "0":
        return -1
    else:
        print("Yanlis Secim ", choise)
        return 0
    print("Ana Menuye Donmek Icin Bir Tusa Basiniz".center(columns))
    input()
default_menu() # Baslatma Fonksiyonunu cagir
