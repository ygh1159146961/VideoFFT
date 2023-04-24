import os
import subprocess
import cv2
import numpy as np


def fft_channel(img):
    # 二维离散傅里叶变换得到图像的频域表示
    img_fft = np.fft.fft2(img)
    img_fft = np.fft.fftshift(img_fft)
    img_magnitude = np.abs(img_fft)
    img_phase = np.angle(img_fft)
    # 幅度谱的范围0~height*width*255，取对数，再乘上系数10，转为图片
    img_magnitude = 10 * np.log(np.abs(img_fft))
    # 相位谱为弧度制-pi~pi，转为0-255之间
    img_magnitude = np.clip(img_magnitude, 0, 255).astype(np.uint8)
    img_phase = (img_phase + np.pi) / (2 * np.pi) * 255
    img_phase = np.clip(img_phase, 0, 255).astype(np.uint8)
    return img_magnitude, img_phase


def fft_img(img):
    # opencv使用BGR通道
    b, g, r = cv2.split(img)
    b_magnitude, b_phase = fft_channel(b)
    g_magnitude, g_phase = fft_channel(g)
    r_magnitude, r_phase = fft_channel(r)
    return cv2.merge([b_magnitude, g_magnitude, r_magnitude]), cv2.merge([b_phase, g_phase, r_phase])


def ifft_channel(img_magnitude, img_phase):
    img_magnitude = np.exp(img_magnitude.astype(float) / 10)
     # 0~255转为-pi~pi
    img_phase = img_phase.astype(float) / 255 * (2 * np.pi) - np.pi
    img_recover = img_magnitude * np.exp(1j * img_phase)
    img_recover = np.fft.ifftshift(img_recover)
    img_recover = np.fft.ifft2(img_recover)
    img_recover = np.clip(np.abs(img_recover), 0, 255).astype(np.uint8)
    return img_recover


def ifft_img(img_magnitude, img_phase):
    b_magnitude, g_magnitude, r_magnitude = cv2.split(img_magnitude)
    b_phase, g_phase, r_phase = cv2.split(img_phase)
    b = ifft_channel(b_magnitude, b_phase)
    g = ifft_channel(g_magnitude, g_phase)
    r = ifft_channel(r_magnitude, r_phase)
    return cv2.merge([b, g, r])


# 将视频转为幅度谱和相位谱
def fft_video(video_dir, output_dir):
    # 读取视频
    print('reading video...')
    video = cv2.VideoCapture(video_dir)
    fps = video.get(cv2.CAP_PROP_FPS)
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # 提取文件名
    video_name = os.path.splitext(os.path.basename(video_dir))[0]
    # 输出图片序列文件夹
    output_magnitude_dir = os.path.join(output_dir, f'{video_name}_magnitude_imgs')
    if not os.path.exists(output_magnitude_dir):
        os.mkdir(output_magnitude_dir)
    output_phase_dir = os.path.join(output_dir, f'{video_name}_phase_imgs')
    if not os.path.exists(output_phase_dir):
        os.mkdir(output_phase_dir)
    print('fft processing...')
    # 逐帧处理并写入文件夹
    i = 0
    while True:
        success, frame = video.read()
        if not success:
            break
        frame_magnitude, frame_phase = fft_img(frame)
        cv2.imwrite(os.path.join(output_magnitude_dir, f'{i}.png'), frame_magnitude)
        cv2.imwrite(os.path.join(output_phase_dir, f'{i}.png'), frame_phase)
        i += 1
    video.release()
    print('ffmpeg from img to video...')
    # 调用ffmpeg将图片拼接为视频，H264编码支持无损视频
    magnitude_cmd = ['ffmpeg', '-r', f'{fps}', '-f', 'image2',
                     '-i', f'{output_magnitude_dir}\\%d.png',
                     '-vcodec', 'libx264', '-crf', '0',
                     f'{output_dir}\\{video_name}_magnitude.avi']
    phase_cmd = ['ffmpeg', '-r', f'{fps}', '-f', 'image2',
                 '-i', f'{output_phase_dir}\\%d.png',
                 '-vcodec', 'libx264', '-crf', '0',
                 f'{output_dir}\\{video_name}_phase.avi']
    subprocess.Popen(magnitude_cmd)
    subprocess.Popen(phase_cmd)
    print('fft video complete.')
    return


# 从幅度谱和相位谱复原视频
def ifft_video(video_magnitude_dir, video_phase_dir, output_dir):
    # 读取视频
    print('reading video...')
    video_magnitude = cv2.VideoCapture(video_magnitude_dir)
    video_phase = cv2.VideoCapture(video_phase_dir)
    fps = video_magnitude.get(cv2.CAP_PROP_FPS)
    width = int(video_magnitude.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video_magnitude.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # 提取文件名
    video_name = os.path.splitext(os.path.basename(video_magnitude_dir))[0][0:-10]
    # 复原视频选择MJPEG编码，兼容Windows Media Player
    fourcc = cv2.VideoWriter_fourcc(*'MP4V')
    output_recover = cv2.VideoWriter(f'{output_dir}\\{video_name}_recover.avi', fourcc, fps, (width, height))
    print('ifft processing...')
    # 逐帧处理并写入文件
    while True:
        success_magnitude, frame_magnitude = video_magnitude.read()
        success_phase, frame_phase = video_phase.read()
        if not (success_magnitude and success_phase):
            break
        frame_recover = ifft_img(frame_magnitude, frame_phase)
        output_recover.write(frame_recover)
    video_magnitude.release()
    video_phase.release()
    output_recover.release()
    print('ifft video complete.')
    return


def fft_process(input_dir, output_dir):
    file_name = os.path.basename(input_dir)
    file_prefix = os.path.splitext(file_name)[0] # 文件名（去除后缀）
    if file_name.endswith(('jpg', 'jpeg', 'png', 'bmp')):
        input_img = cv2.imread(input_dir)
        output_magnitude, output_phase = fft_img(input_img)
        cv2.imwrite(f'{output_dir}\\{file_prefix}_magnitude.png', output_magnitude)
        cv2.imwrite(f'{output_dir}\\{file_prefix}_phase.png', output_phase)
    elif file_name.endswith(('mp4', 'avi', 'mpg', 'mpeg', 'wmv', 'mov')):
        fft_video(input_dir, output_dir)
    return


def ifft_process(input_magnitude_dir, input_phase_dir, output_dir):
    file_name = os.path.basename(input_magnitude_dir)
    # 文件名（去除后缀以及_magnitude）
    file_prefix = os.path.splitext(file_name)[0][0:-10]
    if file_name.endswith(('jpg', 'jpeg', 'png', 'bmp')):
        input_magnitude = cv2.imread(input_magnitude_dir)
        input_phase = cv2.imread(input_phase_dir)
        output_recover = ifft_img(input_magnitude, input_phase)
        cv2.imwrite(f'{output_dir}\\{file_prefix}_recover.png', output_recover)
    elif file_name.endswith(('mp4', 'avi', 'mpg', 'mpeg', 'wmv', 'mov')):
        ifft_video(input_magnitude_dir, input_phase_dir, output_dir)
    return
