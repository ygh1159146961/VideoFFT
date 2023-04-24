import VideoFFT
import cv2
import matplotlib.pyplot as plt


VideoFFT.fft_process(r'test\img.png', r'test')
VideoFFT.ifft_process(r'test\img_magnitude.png', r'test\img_phase.png', r'test')

img_original = cv2.imread(r'test\img.png')
img_original = cv2.cvtColor(img_original, cv2.COLOR_BGR2RGB)
img_recover = cv2.imread(r'test\img_recover.png')
img_recover = cv2.cvtColor(img_recover, cv2.COLOR_BGR2RGB)
img_magnitude = cv2.imread(r'test\img_magnitude.png')
img_magnitude = cv2.cvtColor(img_magnitude, cv2.COLOR_BGR2RGB)
img_phase = cv2.imread(r'test\img_phase.png')
img_phase = cv2.cvtColor(img_phase, cv2.COLOR_BGR2RGB)

plt.figure(figsize=(20, 20))
plt.subplot(2, 2, 1)
plt.title('original image')
plt.imshow(img_original)
plt.subplot(2, 2, 2)
plt.title('recovered image')
plt.imshow(img_recover)
plt.subplot(2, 2, 3)
plt.title('magnitude spectrum')
plt.imshow(img_magnitude)
plt.subplot(2, 2, 4)
plt.title('phase spectrum')
plt.imshow(img_phase)

plt.show()
