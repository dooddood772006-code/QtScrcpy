import re
GET = 'qsc::IDeviceManage::getInstance().getDevice(m_serial)'

def rd(p):
    return open(p, encoding='utf-8').read()

def wr(p, s):
    open(p, 'w', encoding='utf-8').write(s)

def rep(s, old, new, path):
    assert s.count(old) >= 1, (path, old[:60])
    return s.replace(old, new)

p = 'QtScrcpy/ui/toolform.cpp'
wr(p, rd(p).replace(GET, 'currentDevice()'))
p = 'QtScrcpy/ui/toolform.h'
s = rd(p)
s = rep(s, '    QString m_serial;\n', '    QString m_serial;\n    QPointer<qsc::IDevice> m_device;\n', p)
s = rep(s, '    explicit ToolForm(QWidget *adsorbWidget, AdsorbPositions adsorbPos);\n',
        '    explicit ToolForm(QWidget *adsorbWidget, AdsorbPositions adsorbPos);\n'
        '    void setDevice(qsc::IDevice *device) { m_device = device; }\n'
        '    QPointer<qsc::IDevice> currentDevice() const {\n'
        '        return m_device.isNull() ? qsc::IDeviceManage::getInstance().getDevice(m_serial) : m_device;\n'
        '    }\n', p)
wr(p, s)

p = 'QtScrcpy/ui/videoform.cpp'
s = rd(p).replace(GET, 'currentDevice()')
s = rep(s, '        m_toolForm = new ToolForm(this, ToolForm::AP_OUTSIDE_RIGHT);\n',
        '        m_toolForm = new ToolForm(this, ToolForm::AP_OUTSIDE_RIGHT);\n'
        '        if (!m_device.isNull()) {\n            m_toolForm->setDevice(m_device.data());\n        }\n', p)
s += '''
void VideoForm::setDevice(qsc::IDevice *device)
{
    m_device = device;
    if (m_toolForm) {
        m_toolForm->setDevice(device);
    }
}
'''
wr(p, s)
p = 'QtScrcpy/ui/videoform.h'
s = rd(p)
s = rep(s, '    QString m_serial;\n', '    QString m_serial;\n    QPointer<qsc::IDevice> m_device;\n', p)
s = rep(s, '    explicit VideoForm(bool framelessWindow = false, bool skin = true, bool showToolBar = true, int decodeMode = 0, QWidget *parent = 0);\n',
        '    explicit VideoForm(bool framelessWindow = false, bool skin = true, bool showToolBar = true, int decodeMode = 0, QWidget *parent = 0);\n'
        '    void setDevice(qsc::IDevice *device);\n'
        '    QPointer<qsc::IDevice> currentDevice() const {\n'
        '        return m_device.isNull() ? qsc::IDeviceManage::getInstance().getDevice(m_serial) : m_device;\n'
        '    }\n', p)
wr(p, s)

p = 'QtScrcpy/ui/dialog.h'
s = rd(p)
s = rep(s, '    void onDeviceConnected(bool success, const QString& serial, const QString& deviceName, const QSize& size);\n',
        '    void onDeviceConnected(bool success, const QString& serial, const QString& deviceName, const QSize& size);\n'
        '    void onSecondaryDeviceConnected(bool success, const QString& serial, const QSize& size, qsc::IDevice* device);\n', p)
wr(p, s)
p = 'QtScrcpy/ui/dialog.cpp'
s = rd(p)
s = rep(s, '    connect(&qsc::IDeviceManage::getInstance(), &qsc::IDeviceManage::deviceConnected, this, &Dialog::onDeviceConnected);\n',
        '    connect(&qsc::IDeviceManage::getInstance(), &qsc::IDeviceManage::deviceConnected, this, &Dialog::onDeviceConnected);\n'
        '    connect(&qsc::IDeviceManage::getInstance(), &qsc::IDeviceManage::secondaryDeviceConnected, this, &Dialog::onSecondaryDeviceConnected);\n', p)
s += '''
void Dialog::onSecondaryDeviceConnected(bool success, const QString &serial, const QSize &size, qsc::IDevice *device)
{
    if (!success || !device) {
        return;
    }
    auto videoForm = new VideoForm(ui->framelessCheck->isChecked(), Config::getInstance().getSkin(), ui->showToolbar->isChecked(), ui->decodeModeBox->currentIndex());
    videoForm->setSerial(serial);
    videoForm->setDevice(device);
    device->setUserData(static_cast<void*>(videoForm));
    device->registerDeviceObserver(videoForm);
    videoForm->showFPS(ui->fpsCheck->isChecked());
    videoForm->setWindowTitle(serial + " - main screen");
    videoForm->updateShowSize(size);
    videoForm->show();
}
'''
wr(p, s)
print("ui edits ok")
