# VideoFFT
将图片/视频通过快速傅里叶变换转为幅度谱和相位谱，并从幅度谱和相位谱复原图片/视频

![result.png](https://github.com/Matoi647/VideoFFT/blob/main/test/result.png)

## 使用方法
首先安装numpy和opencv-python
```
pip install numpy opencv-python
```
克隆项目
```
git clone https://github.com/Matoi647/VideoFFT.git
```

```
import VideoFFT
# IMAGE_OR_VIDEO_PATH: 图片或视频的路径
# OUTPUT_PATH: 输出路径
# MAGNITUDE_SPECTRUM_PATH: 生成的幅度谱路径
# PHASE_SPECTRUM_PATH: 生成的相位谱路径

# 傅里叶变换
VideoFFT.fft_process(r'IMAGE_OR_VIDEO_PATH', r'OUTPUT_PATH')
# 傅里叶逆变换
# VideoFFT.ifft_process(r'MAGNITUDE_SPECTRUM_PATH', r'PHASE_SPECTRUM_PATH', r'OUTPUT_PATH')
```

## 局限性
由于幅度谱和相位谱对于图片的精度要求很高，采用了无损压缩，导致产生的视频文件体积很大

1920x1080,30fps,1分钟的原视频，生成的幅度谱和相位谱视频为10G左右

如果使用压缩后的幅度谱和相位谱复原，得到的效果如下
![compressed_recover](https://github.com/Matoi647/VideoFFT/blob/main/test/compressed_img_recover.png)
