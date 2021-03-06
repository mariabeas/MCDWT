import numpy as np
import cv2
import pywt

def split_video_in_frames_to_disk(filename):
    '''
    Reads a video file frame by frame, convert each frame to
    YCrCb and saves it in the folder /output as a binaryfile with
    .npy extension.
    '''
    cap = cv2.VideoCapture(filename)
    num_frame = 0

    while(cap.isOpened()):

        ret, frame = cap.read()
        if frame is None:
            break

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)


        cv2.imwrite('test_images/'+str(num_frame)+'.png',image)
        
        num_frame = num_frame + 1


def read_frame(filename):
    '''
    Reads a frame from a filename.
    '''

    # To see it in RGB uncomment the next line
    # image = cv2.cvtColor(image, cv2.COLOR_YCrCb2BGR)

    return cv2.imread(filename,1)

def image_to_dwt2d(image):
    '''
    Compute the 1-level 2D-DWT of a frame in memory.
    '''
    coeffs = pywt.dwt2(image, 'haar')
    
    return coeffs



def dwt2d_to_image(coeffs):
    '''
    Compute to a frame the 1-level 2D-DWT
    '''
    image = pywt.idwt2(coeffs, 'haar')
    
    return image

def forward_MCDWT(imageA, imageB, imageC):

    height = imageA.shape[0]
    width = imageA.shape[1]
    coeffA=image_to_dwt2d(imageA[:,:,0])
    coeffB=image_to_dwt2d(imageB[:,:,0])
    coeffC=image_to_dwt2d(imageC[:,:,0])
    
    All = coeffA[0]
    Ahl = coeffA[1][0]
    Alh = coeffA[1][1]
    Ahh = coeffA[1][2]

    Bll = coeffB[0]
    Bhl = coeffB[1][0]
    Blh = coeffB[1][1]
    Bhh = coeffB[1][2]

    Cll = coeffC[0]
    Chl = coeffC[1][0]
    Clh = coeffC[1][1]
    Chh = coeffC[1][2]
    
    zeroes = np.zeros((height//2, width//2), dtype="float64")
        
    iAl = dwt2d_to_image((All,(zeroes,zeroes,zeroes)))
    iAh = dwt2d_to_image((zeroes,(Ahl,Alh,Ahh)))


    iBl = dwt2d_to_image((Bll,(zeroes,zeroes,zeroes)))
    iBh = dwt2d_to_image((zeroes,(Bhl,Blh,Bhh)))


    iCl = dwt2d_to_image((Cll,(zeroes,zeroes,zeroes)))
    iCh = dwt2d_to_image((zeroes,(Chl,Clh,Chh)))


    imagenResiduo = iBh-((iAh + iCh)/2)

    coeffR = image_to_dwt2d(imagenResiduo)
    
    Rll = coeffR[0]
    Rhl = coeffR[1][0]
    Rlh = coeffR[1][1]
    Rhh = coeffR[1][2]

    Rll = Bll

    outputA = np.zeros((height, width), dtype="int16")
    outputA[0:height//2, 0:width//2] = All
    outputA[0:height//2, width//2:width] = Ahl
    outputA[height//2:height, 0:width//2] = Alh
    outputA[height//2:height, width//2:width] = Ahh

    outputC = np.zeros((height, width), dtype="int16")
    outputC[0:height//2, 0:width//2] = Cll
    outputC[0:height//2, width//2:width] = Chl
    outputC[height//2:height, 0:width//2] = Clh
    outputC[height//2:height, width//2:width] = Chh

    outputR = np.zeros((height, width), dtype="int16")
    outputR[0:height//2, 0:width//2] = Rll
    outputR[0:height//2, width//2:width] = Rhl
    outputR[height//2:height, 0:width//2] = Rlh
    outputR[height//2:height, width//2:width] = Rhh

    # cv2.imwrite('test_images/A.png',outputA)
    # cv2.imwrite('test_images/R.png',outputR)
    # cv2.imwrite('test_images/C.png',outputC)

    return outputA, outputR, outputC

def video_converter (file_in, file_out):

    cap = cv2.VideoCapture(file_in)
    ret, frame1 = cap.read()

    fourcc = cv2.VideoWriter_fourcc(*'X264')
    out = cv2.VideoWriter(file_out,fourcc, 50.0, (frame1.shape[0],frame1.shape[1]), False)


    while(cap.isOpened()):

        ret, frame2 = cap.read()
        ret, frame3 = cap.read()
        
        if frame3 is None or frame2 is None or frame3 is None :
            break
        image1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2YCrCb)
        image2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2YCrCb)
        image3 = cv2.cvtColor(frame3, cv2.COLOR_BGR2YCrCb)

        image1, image2, image3 = forward_MCDWT(image1,image2,image3)
        
        image1 = 256*((image1+512)/1024)
        image2 = 256*((image2+512)/1024)
        image3 = 256*((image3+512)/1024)

        image1 = np.uint8(image1)
        image2 = np.uint8(image2)
        image3 = np.uint8(image3)


        out.write(image1)
        out.write(image2)
        out.write(image3)
        frame1 = frame3

    cap.release()
    out.release()

# forward_MCDWT(read_frame('output/PNG/imagen56.png'),read_frame('output/PNG/imagen57.png'),read_frame('output/PNG/imagen58.png'))

# read_video('stockholm_1280x768x50x420x578.avi')

# image = read_frame('output/stockholm_1280x768x50x420x578.avi13.npy')   
# cv2.imshow('image', image)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# image = read_frame('output/stockholm_1280x768x50x420x578.avi13.npy') 
# image = dwt2d_to_image(image_to_dwt2d(image))  
# cv2.imshow('image', image)
# cv2.waitKey(0)
# cv2.destroyAllWindows()