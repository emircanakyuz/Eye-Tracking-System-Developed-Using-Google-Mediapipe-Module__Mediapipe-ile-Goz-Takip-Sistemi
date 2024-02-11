import cv2 as cv
import numpy as np
import mediapipe as mp
import pygame

# Pencere boyutları
window_width, window_height = 800, 600
plane_x, plane_y = window_width // 2, window_height // 2
plane_speed_x, plane_speed_y = 20, 20

# Uçak resmini yükle ve boyutunu ayarla
plane_image = pygame.image.load("savas_ucagi.png")
plane_image = pygame.transform.scale(plane_image, (200, 200))

# Arkaplan resmini yükle
background_image = pygame.image.load("arkaplan.png")

# Göz ve İris koordinatlarımız
left_eye=[362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
right_eye=[33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
right_iris=[469, 470, 471, 472]
left_iris=[474, 475, 476, 477]

mp_face_mesh=mp.solutions.face_mesh

#Kamera ayarları
cap=cv.VideoCapture(0) #0 numaralı kamerayı kullan  
with mp_face_mesh.FaceMesh( #with bloğu
    max_num_faces=1, #Tespit edilecek yüz sayısı
    refine_landmarks=True, #Yüz noktaları daha hassas belirlensin mi? True.
    min_detection_confidence=0.5, #Tespit olasılığı
    min_tracking_confidence=0.5) as face_mesh:

    # Pygame penceresini başlat
    pygame.init()
    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Uçak Oyunu")

    # Gözlerimizin baktığı ortak x ve y noktaları için ilk değişken ataması gerçekleştiriyoruz.
    common_x_points_eyes = window_width // 2 
    common_y_points_eyes = window_height // 2


    while True:
        '''
        Kameradan bir kare yakalar ve ret değişkenine başarı durumunu (True veya False) atar,
        aynı zamanda frame değişkenine görüntüyü atar.
        '''
        ret, frame=cap.read()   
        if not ret:
            break
        rgb_frame=cv.cvtColor(frame,cv.COLOR_BGR2RGB) #BGR renk uzayını RGB renk uzayına doğru çevirir.
        camera_height,camera_width=frame.shape[:2] #frame.shape ifadesi, görüntünün boyutlarıyla ilgili bilgileri içeren bir tuple döndürür. Bu tuple'ın ilk iki elemanı sırasıyla yükseklik ve genişliği temsil eder.
        results=face_mesh.process(rgb_frame)
        if results.multi_face_landmarks:

            '''
            Bu satır, her bir landmark noktasının normalize edilmiş x ve y koordinatlarını görüntünün boyutlarıyla çarpar ve sonuçları tam sayıya dönüştürür.
            Bu sayede, landmark noktalarının piksel koordinatları elde edilir.
            Bu piksel koordinatları, daha sonra görüntü üzerinde çeşitli çizim veya işlemler için kullanılabilir.
            '''
            mesh_points=np.array([np.multiply([p.x,p.y],[camera_width,camera_height]).astype(int) for p in results.multi_face_landmarks[0].landmark])

            # uçağı hareket ettir
            plane_x += plane_speed_x
            plane_y += plane_speed_y

            # Eğer uçak pencerenin dışına çıkarsa, hızını tersine çevir
            if plane_x <= 0 or plane_x >= window_width:
                plane_speed_x *= -1
            if plane_y <= 0 or plane_y >= window_height:
                plane_speed_y *= -1

            # Gözün baktığı noktayı uçağın konumu olarak ayarla
            plane_x = common_x_points_eyes
            plane_y = common_y_points_eyes    

            # Pencereyi temizle
            screen.fill((0, 0, 0))

            # Arkaplanı ve uçağı ekrana yerleştir.
            screen.blit(background_image, (0, 0))
            screen.blit(plane_image, (plane_x, plane_y))

            # Pencereyi güncelle
            pygame.display.flip()

            # Kullanıcı kapatma işlemi yaparsa döngüden çık
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    break

            '''
            Yularıdaki satır, görüntünün boyutlarına göre normalize edilmiş
            ve tam sayıya dönüştürülmüş şekilde elde edilen landmark noktalarını içeren
            bir NumPy array'ini temsil eder.
            '''
            # Gözkapaklarına bir cizgi cizer 
            cv.polylines(frame, [mesh_points[right_eye]], True, (0,255,0), 1, cv.LINE_AA) 
            cv.polylines(frame, [mesh_points[left_eye]], True, (0,255,0), 1, cv.LINE_AA)
            
            # X ve Y Koordinatlarının merkezdeki en küçük çemberin yarıçapını ve gerekli atamaları yapar.
            (r_cx, r_cy), r_radius=cv.minEnclosingCircle(mesh_points[right_iris])
            (l_cx, l_cy), l_radius=cv.minEnclosingCircle(mesh_points[left_iris])
            
            '''
            En küçük çemberi kullanmamın sebebi, irislerin şeklini ve konumunu daha iyi belirlemek içindir.
            Irisler, yüz örgüsü modelinde dört noktadan oluşan bir dörtgen olarak tanımlanır.
            Bu dört nokta, irislerin tamamını kapsamayabilir veya irislerin yuvarlak olmadığını varsayabilir.
            Bu nedenle, irislerin etrafına en küçük çemberi çizerek, irislerin gerçek boyutunu,
            merkezini ve yönünü daha doğru bir şekilde hesaplayabiliriz.
            '''
            center_right=np.array([r_cx,r_cy], dtype=np.int32)
            center_left=np.array([l_cx,l_cy], dtype=np.int32)
            cv.circle(frame, center_right, int(r_radius), (255,0,255), 1, cv.LINE_AA)
            cv.circle(frame, center_left, int(l_radius), (255,0,255), 1, cv.LINE_AA)
            print("x and Y Coordinates Of The Left Eye: " , center_left, "X and Y Coordinates Of The Right Eye: ", center_right, "Common X and Y Coordinates Of The Eye: ", common_x_points_eyes, common_y_points_eyes)
            common_x_points_eyes=(int((center_right[0]+center_left[0])/2))
            common_y_points_eyes=(int((center_right[1]+center_left[1])/2))
            
            '''
            ÖNEMLİ: X,Y ve Z olamk üzere 3 çeşit noktalama listesi oluşturlacak. X, yatay eksendedki koordinatsal noktalamayı gösterirken;
            Y, dikey eksendedki koordinatsal noktalamayı gösterir. 3D çalışma alanlarında derinliği ifade eder
            fakat biz 2D olan bir çalışma ortamında olacağımız için Z değerine ihtiyacımız olmayacak.
            '''   
        cv.imshow('camera',frame)
        key=cv.waitKey(1)
        if key == 27:
            break
        
pygame.quit() 
cap.release()
cv.destroyAllWindows()

