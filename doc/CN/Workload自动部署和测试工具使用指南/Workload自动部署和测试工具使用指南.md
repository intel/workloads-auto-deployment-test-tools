# Workload自动部署和测试工具使用指南

## 1. 系统架构简介

该系统由两部分组成：

- Web前端界面，运用主流的VueJS+Django的前端框架，开发出一套友好的用户界面，用于选择需要的workload，以及他需要运行的目标机器，并定制对目标机器的环境配置。

- 后端服务，主要用go和python开发。前端的定制需求，通过配置的形式传输给后端，后端调用ansible，在目标机器把workload需要运行起来的所有环境配置好，包括k8s安装，内核参数修改，内核版本替换等。等所有环境准备就绪后，后端会调用jenkins服务器，把workload运行起来，并最终得到KPI。

###### ![Diagram Description automatically generated](media/image1.png)

## 2. 系统使用指南

### 2.1 登录系统

2.1.1 在服务器端，输入命令docker exec -it backend bash，进入django后端管理docker容器。

2.1.2 输入命令python manage.py createsuperuser，创建管理员账户。

2.1.3 浏览器输入http://{服务器IP地址}:8899/，用创建的管理员账户登录。

### 2.2 录入机器信息

2.2.1 点击导航页面admin，进入到后台控制界面。![](media/image2.png)

2.2.2 点击“Local instance”,进入机器录入界面。![](media/image3.png)

2.2.3 点击“ADD LOCAL INSTANCE”录入机器信息。![](media/image4.png)

### 2.3 创建任务

2.3.1 从主页点击“Local”-\>”Provision”进入创建任务菜单，选择workload和配置的版本，系统默认录入的配置名是config1。![](media/image5.png)

2.3.2 点击下一步，选择workload的目标机器，并选择需要运行的时间，如果该时间段机器可用，则可以下一步继续配置，若机器已经被使用，则需要另外选择时间段，直到通过验证。![](media/image6.png)

2.3.3 点击下一步，选择是否需要在目标机器部署k8s，该选项默认是关闭，如需配置点击开关打开，依次填入选项。![](media/image7.png)

2.3.4 点击下一步，如果在上一步的“kubernetes install method”上选择了vm，则需填入vm的参数，否则该按钮为灰色，可以跳过。![](media/image8.png)

2.3.5 点击下一步，在“JSF Repo”填入WSF的github地址，若无特殊要求，使用默认值即可；在“Commit”填入WSF的github地址的提交id，若无特殊要求，使用默认值即可；在“Registry”下拉框选择docker镜像的registry；在“case filter”栏填入需要执行的KPI用例，若为空则会执行全部用例，支持正则表达式输入；在“Workload Parameters
”填入需要的参数，该选项为选填项，需要根据workload的文档来确定是否需要填写，格式为“PARAMETER_NAME1=xxx PARAMETER_NAME2=xxx”。![](media/image9.png)

2.3.6 点击下一步，该选项为特殊的workload配置需要，保持默认关闭状态即可。![](media/image10.png)

2.3.7 点击下一步，根据workload的说明文档，如果需要则打开配置，目前支持配置“Kernel update”，“Kernel args update”， 即将支持“BIOS update”。![](media/image11.png)

2.3.8 点击下一步，“Receiver Email”填入需要接收KPI结果邮箱的地址，“Sender Email”填入发送方地址。该功能需要用户自己拥有邮件服务器，邮件服务器地址的配置在系统部署指南里面有提及。![](media/image12.png)

2.3.9 点击submit提交，系统会自动导航到任务栏。![](media/image13.png)

### 2.4 查看任务结果

2.4.1 点击“Job”菜单，系统会实时更新任务状态和进度

2.4.2 点击“Log”可实时查看任务执行状态

![](media/image14.png)

## 附录

如果当时使用的 Workload 为 Smart-Sport-Analyzer，则在 Provision 填写时 Workload Args 部分会出现 Upload video files 功能，提示上传视频文件。当按照要求选择文件并上传后，会提示上传进度。如下图所示 

![](media/image15.png)

注意：在使用该 Workload 时需要修改 `WSF-VAAS/portal/backend/taas/` 目录下 `settings_dev_docker.py`, `setting_dev.py` 以及 `setting.py` 文件中 `DEBUG = False` 改为 `DEBUG = True`。