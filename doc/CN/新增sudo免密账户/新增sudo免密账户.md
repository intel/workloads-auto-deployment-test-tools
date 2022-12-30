# 新增sudo免密账户

## 1. 检查当前用户

###### ![](media/image1.png)

## 2. 创建一个用户，假定名字是username

```shell
useradd -m username
```

## 3. 为新用户设置密码

```shell
passwd username
```

###### ![](media/image2.png)

## 4. 授予新用户sudo免密权限

### 4.1 切换到root用户

```shell
su root
```

###### ![](media/image3.png)

###### ![](media/image4.png)

### 4.2 增加写权限

```shell
chmod u+w /etc/sudoers
```

###### ![](media/image5.png)

### 4.3 编辑文件/etc/sudoers

```shell
vim /etc/sudoers
```

添加username的sudo免密配置，如图红色框所示

###### ![](media/image6.png)

### 4.4 取消/etc/sudoers的可写权限

```shell
chmod u-w /etc/sudoers
```

## 5. 检查是否配置成功

###### ![](media/image7.png)
