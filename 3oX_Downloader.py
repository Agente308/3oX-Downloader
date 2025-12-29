import os, certifi
os.environ["SSL_CERT_FILE"] = certifi.where()

import yt_dlp
import sys
import json
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QLabel, QLineEdit, QPushButton, 
    QRadioButton, QButtonGroup, QFileDialog, QProgressBar,
    QMessageBox, QFrame, QGroupBox, QDialog, QSpinBox,
    QComboBox, QCheckBox, QScrollArea
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize, QRect
from PyQt5.QtGui import (
    QFont, QIcon, QPixmap, QPainter, QPainterPath,
    QColor, QPen
)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class DiagonalGroupBox(QGroupBox):
    def __init__(self, title="", parent=None):
        super().__init__(title, parent)
        self.setStyleSheet("")
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        rect = self.rect()
        corner_size = 10
        title_height = 30
        cut_size = 8
        
        fm = painter.fontMetrics()
        title_width = fm.horizontalAdvance(self.title()) + 24
        title_x = 15

        main_path = QPainterPath()
        main_path.moveTo(corner_size, title_height)
        main_path.lineTo(rect.right() - corner_size, title_height)
        main_path.lineTo(rect.right(), title_height + corner_size)
        main_path.lineTo(rect.right(), rect.bottom() - corner_size)
        main_path.lineTo(rect.right() - corner_size, rect.bottom())
        main_path.lineTo(corner_size, rect.bottom())
        main_path.lineTo(0, rect.bottom() - corner_size)
        main_path.lineTo(0, title_height + corner_size)
        main_path.lineTo(corner_size, title_height)
        
        painter.fillPath(main_path, QColor("#181825"))
        painter.setPen(QPen(QColor("#4a5568"), 1))
        painter.drawPath(main_path)
        
        title_path = QPainterPath()
        title_path.moveTo(title_x, title_height - 2)
        title_path.lineTo(title_x, cut_size)
        title_path.lineTo(title_x + cut_size, 0)
        title_path.lineTo(title_x + title_width - cut_size, 0)
        title_path.lineTo(title_x + title_width, cut_size)
        title_path.lineTo(title_x + title_width, title_height - 2)
        title_path.lineTo(title_x, title_height - 2)
        
        painter.fillPath(title_path, QColor("#1e2837"))
        painter.setPen(QPen(QColor("#5a8cdb"), 1.5))
        painter.drawPath(title_path)
        
        painter.setPen(QColor("#89b4fa"))
        painter.setFont(QFont("Segoe UI", 10, QFont.Bold))
        title_rect = QRect(title_x, 0, title_width, title_height - 2)
        painter.drawText(title_rect, Qt.AlignCenter, self.title())

class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setWindowTitle("Configuracion")
        self.setFixedSize(620, 990)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(18)
        layout.setContentsMargins(25, 25, 25, 25)
        
        title = QLabel("Configuracion")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #89b4fa; margin-bottom: 15px;")
        layout.addWidget(title)
        
        hilos_group = DiagonalGroupBox("Hilos de Descarga")
        hilos_group.setFont(QFont("Segoe UI", 11, QFont.Bold))
        hilos_layout = QVBoxLayout()
        hilos_layout.setSpacing(12)
        hilos_layout.setContentsMargins(20, 40, 20, 20)
        
        hilos_label = QLabel("Numero de hilos simultaneos:")
        hilos_label.setFont(QFont("Segoe UI", 10))
        hilos_label.setStyleSheet("color: #cdd6f4;")
        hilos_layout.addWidget(hilos_label)
        
        self.hilos_spin = QSpinBox()
        self.hilos_spin.setMinimum(1)
        self.hilos_spin.setMaximum(32)
        self.hilos_spin.setValue(self.parent_window.config.get('hilos', 16))
        self.hilos_spin.setFont(QFont("Segoe UI", 11))
        self.hilos_spin.setFixedHeight(40)
        hilos_layout.addWidget(self.hilos_spin)
        
        hilos_group.setLayout(hilos_layout)
        layout.addWidget(hilos_group)
        
        ffmpeg_group = DiagonalGroupBox("Ruta de FFmpeg")
        ffmpeg_group.setFont(QFont("Segoe UI", 11, QFont.Bold))
        ffmpeg_layout = QVBoxLayout()
        ffmpeg_layout.setSpacing(12)
        ffmpeg_layout.setContentsMargins(20, 40, 20, 20)
        
        ffmpeg_label = QLabel("Carpeta donde se encuentra ffmpeg.exe:")
        ffmpeg_label.setFont(QFont("Segoe UI", 10))
        ffmpeg_label.setStyleSheet("color: #cdd6f4;")
        ffmpeg_layout.addWidget(ffmpeg_label)
        
        ffmpeg_input_layout = QHBoxLayout()
        ffmpeg_input_layout.setSpacing(10)
        
        self.ffmpeg_input = QLineEdit()
        self.ffmpeg_input.setText(self.parent_window.config.get('ffmpeg_path', ''))
        self.ffmpeg_input.setFont(QFont("Segoe UI", 10))
        self.ffmpeg_input.setFixedHeight(40)
        self.ffmpeg_input.setCursorPosition(0)
        self.ffmpeg_input.textChanged.connect(lambda: self.ffmpeg_input.setCursorPosition(0))
        ffmpeg_input_layout.addWidget(self.ffmpeg_input)
        
        ffmpeg_btn = QPushButton("Examinar")
        ffmpeg_btn.setFixedSize(120, 40)
        ffmpeg_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        ffmpeg_btn.clicked.connect(self.seleccionar_ffmpeg)
        ffmpeg_input_layout.addWidget(ffmpeg_btn)
        
        ffmpeg_layout.addLayout(ffmpeg_input_layout)
        ffmpeg_group.setLayout(ffmpeg_layout)
        layout.addWidget(ffmpeg_group)
        
        limite_group = DiagonalGroupBox("Limite de Velocidad")
        limite_group.setFont(QFont("Segoe UI", 11, QFont.Bold))
        limite_layout = QVBoxLayout()
        limite_layout.setSpacing(12)
        limite_layout.setContentsMargins(20, 40, 20, 20)
        
        self.limite_check = QCheckBox("Limitar velocidad de descarga")
        self.limite_check.setFont(QFont("Segoe UI", 10))
        self.limite_check.setStyleSheet("color: #cdd6f4;")
        self.limite_check.setChecked(self.parent_window.config.get('limite_enabled', False))
        self.limite_check.stateChanged.connect(self.toggle_limite)
        limite_layout.addWidget(self.limite_check)
        
        limite_input_layout = QHBoxLayout()
        limite_input_layout.setSpacing(10)
        
        limite_input_label = QLabel("Velocidad maxima:")
        limite_input_label.setFont(QFont("Segoe UI", 10))
        limite_input_label.setStyleSheet("color: #cdd6f4;")
        limite_input_layout.addWidget(limite_input_label)
        
        self.limite_spin = QSpinBox()
        self.limite_spin.setMinimum(1)
        self.limite_spin.setMaximum(10000)
        self.limite_spin.setValue(self.parent_window.config.get('limite_mbps', 10))
        self.limite_spin.setSuffix(" Mbps")
        self.limite_spin.setFont(QFont("Segoe UI", 10))
        self.limite_spin.setFixedHeight(40)
        self.limite_spin.setFixedWidth(150)
        self.limite_spin.setEnabled(self.limite_check.isChecked())
        limite_input_layout.addWidget(self.limite_spin)
        limite_input_layout.addStretch()
        
        limite_layout.addLayout(limite_input_layout)
        limite_group.setLayout(limite_layout)
        layout.addWidget(limite_group)

        cookies_group = DiagonalGroupBox("Cookies del Navegador")
        cookies_group.setFont(QFont("Segoe UI", 11, QFont.Bold))
        cookies_layout = QVBoxLayout()
        cookies_layout.setSpacing(12)
        cookies_layout.setContentsMargins(20, 40, 20, 20)
        
        cookies_label = QLabel("Usar cookies para evitar errores 403:")
        cookies_label.setFont(QFont("Segoe UI", 10))
        cookies_label.setStyleSheet("color: #cdd6f4;")
        cookies_layout.addWidget(cookies_label)
        
        self.cookies_combo = QComboBox()
        self.cookies_combo.setFont(QFont("Segoe UI", 10))
        self.cookies_combo.setFixedHeight(40)
        navegadores = ["Ninguno", "Chrome", "Firefox", "Edge", "Opera", "Safari"]
        self.cookies_combo.addItems(navegadores)
        cookies_actual = self.parent_window.config.get('cookies_browser', 'Ninguno')
        index = self.cookies_combo.findText(cookies_actual)
        if index >= 0:
            self.cookies_combo.setCurrentIndex(index)
        cookies_layout.addWidget(self.cookies_combo)
        
        cookies_group.setLayout(cookies_layout)
        layout.addWidget(cookies_group)

        tema_group = DiagonalGroupBox("Tema de Colores")
        tema_group.setFont(QFont("Segoe UI", 11, QFont.Bold))
        tema_layout = QVBoxLayout()
        tema_layout.setSpacing(12)
        tema_layout.setContentsMargins(20, 40, 20, 20)
        
        tema_label = QLabel("Seleccionar tema:")
        tema_label.setFont(QFont("Segoe UI", 10))
        tema_label.setStyleSheet("color: #cdd6f4;")
        tema_layout.addWidget(tema_label)
        
        self.tema_combo = QComboBox()
        self.tema_combo.setFont(QFont("Segoe UI", 10))
        self.tema_combo.setFixedHeight(40)
        temas = ["Azul", "Rojo", "Amarillo", "Verde", "Naranja", "Morado", 
                 "Rosa", "Cafe", "Negro", "Blanco", "Gris", "Violeta", 
                 "Cian", "Magenta", "Turquesa", "Beige", "Plateado", "Dorado"]
        self.tema_combo.addItems(temas)
        tema_actual = self.parent_window.config.get('tema', 'Azul')
        index = self.tema_combo.findText(tema_actual)
        if index >= 0:
            self.tema_combo.setCurrentIndex(index)
        tema_layout.addWidget(self.tema_combo)
        
        tema_group.setLayout(tema_layout)
        layout.addWidget(tema_group)
        
        layout.addStretch()
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        cancelar_btn = QPushButton("Cancelar")
        cancelar_btn.setFixedHeight(48)
        cancelar_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        cancelar_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancelar_btn)
        
        guardar_btn = QPushButton("Guardar")
        guardar_btn.setFixedHeight(48)
        guardar_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        guardar_btn.clicked.connect(self.guardar_config)
        btn_layout.addWidget(guardar_btn)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        self.aplicar_estilo()
        
    def toggle_limite(self, state):
        self.limite_spin.setEnabled(state == Qt.Checked)
        
    def seleccionar_ffmpeg(self):
        carpeta = QFileDialog.getExistingDirectory(
            self, "Seleccionar carpeta de FFmpeg", self.ffmpeg_input.text()
        )
        if carpeta:
            self.ffmpeg_input.setText(carpeta)
    
    def guardar_config(self):
        self.parent_window.config['hilos'] = self.hilos_spin.value()
        self.parent_window.config['ffmpeg_path'] = self.ffmpeg_input.text()
        self.parent_window.config['limite_enabled'] = self.limite_check.isChecked()
        self.parent_window.config['limite_mbps'] = self.limite_spin.value()
        self.parent_window.config['cookies_browser'] = self.cookies_combo.currentText()
        self.parent_window.config['tema'] = self.tema_combo.currentText()
        
        self.parent_window.guardar_configuracion()
        self.parent_window.aplicar_tema()
        
        QMessageBox.information(self, "Configuracion", 
                              "Configuracion guardada exitosamente")
        self.accept()
    
    def aplicar_estilo(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e2e;
            }
            QLabel {
                color: #cdd6f4;
            }
            QLineEdit, QSpinBox {
                background-color: #313244;
                color: #cdd6f4;
                border: 2px solid #45475a;
                border-radius: 8px;
                padding: 10px;
                font-size: 11px;
            }
            QLineEdit:focus, QSpinBox:focus {
                border: 2px solid #89b4fa;
            }
            QPushButton {
                background-color: #74c7ec;
                color: #1e1e2e;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #89b4fa;
            }
            QPushButton:pressed {
                background-color: #5ea3d4;
            }
            QComboBox {
                background-color: #313244;
                color: #cdd6f4;
                border: 2px solid #45475a;
                border-radius: 8px;
                padding: 10px 12px;
                font-size: 11px;
            }
            QComboBox:focus {
                border: 2px solid #89b4fa;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #cdd6f4;
                margin-right: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: #313244;
                color: #cdd6f4;
                selection-background-color: #89b4fa;
                selection-color: #1e1e2e;
                border: 2px solid #45475a;
                border-radius: 8px;
                padding: 5px;
            }
            QCheckBox {
                color: #cdd6f4;
                font-size: 11px;
                spacing: 10px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border-radius: 4px;
                border: 2px solid #45475a;
                background-color: #313244;
            }
            QCheckBox::indicator:checked {
                background-color: #89b4fa;
                border: 2px solid #89b4fa;
            }
            QCheckBox::indicator:hover {
                border: 2px solid #74c7ec;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: #45475a;
                border: none;
                border-radius: 4px;
                width: 20px;
                height: 18px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #585b70;
            }
            QSpinBox::up-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-bottom: 5px solid #cdd6f4;
            }
            QSpinBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #cdd6f4;
            }
        """)

class DescargadorThread(QThread):
    progreso = pyqtSignal(str)
    completado = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, url, carpeta, formato, calidad, config):
        super().__init__()
        self.url = url
        self.carpeta = carpeta
        self.formato = formato
        self.calidad = calidad
        self.config = config
    
    def get_opciones_base(self):
        """Retorna opciones base mejoradas para evitar error 403"""
        opciones = {
            'outtmpl': f'{self.carpeta}/%(title)s.%(ext)s',
            'quiet': False,
            'no_warnings': False,
            'concurrent_fragment_downloads': self.config.get('hilos', 16),
            'nocheckcertificate': True,
            'no_check_certificate': True,
            'prefer_insecure': False,
            'extractor_retries': 5,
            'fragment_retries': 5,
            'retries': 10,
            'sleep_interval': 1,
            'max_sleep_interval': 5,
            'skip_unavailable_fragments': True,
            'geo_bypass': True,
            'geo_bypass_country': 'US',
            'allow_unplayable_formats': False,
            'extract_flat': False,
            'cachedir': os.path.join(os.path.dirname(os.path.abspath(__file__)), '.cache'),
            'merge_output_format': 'mp4',
        }
        
        ffmpeg_path = self.config.get('ffmpeg_path', '')
        if ffmpeg_path:
            ffmpeg_exe = os.path.join(ffmpeg_path, 'ffmpeg.exe')
            if os.path.exists(ffmpeg_exe):
                opciones['ffmpeg_location'] = ffmpeg_path
                print(f"[INFO] FFmpeg encontrado en: {ffmpeg_path}")
            else:
                print(f"[WARNING] No se encontro ffmpeg.exe en: {ffmpeg_path}")
                print(f"[INFO] Buscando ffmpeg en PATH del sistema...")
                try:
                    import subprocess
                    result = subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=2)
                    if result.returncode == 0:
                        print(f"[INFO] FFmpeg encontrado en PATH del sistema")
                except:
                    print(f"[WARNING] FFmpeg no encontrado. Los videos pueden estar corruptos.")
        else:
            print(f"[INFO] Ruta de FFmpeg no configurada - intentando usar PATH del sistema")
        
        opciones['http_headers'] = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        cookies_browser = self.config.get('cookies_browser', 'Ninguno')
        cookies_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cookies.txt')
        
        if os.path.exists(cookies_file):
            print(f"[INFO] Usando archivo de cookies: {cookies_file}")
            opciones['cookiefile'] = cookies_file
        elif cookies_browser != 'Ninguno':
            try:
                browser = cookies_browser.lower()
                print(f"[INFO] Extrayendo cookies de {browser}...")
                opciones['cookiesfrombrowser'] = (browser,)
                print(f"[INFO] Cookies configuradas - yt-dlp usara clientes compatibles automaticamente")
            except Exception as e:
                print(f"[WARNING] No se pudieron configurar cookies: {e}")
        else:
            print(f"[INFO] Sin cookies - usando clientes por defecto")
        
        return opciones
    
    def configurar_plataforma(self, opciones):
        """Configura opciones especificas segun la plataforma"""
        url_lower = self.url.lower()
        
        if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
            cookies_browser = self.config.get('cookies_browser', 'Ninguno')
            cookies_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cookies.txt')
            
            if cookies_browser == 'Ninguno' and not os.path.exists(cookies_file):
                print("[INFO] Sin cookies - usando clientes android/ios")
                opciones['extractor_args'] = {
                    'youtube': {
                        'player_client': ['android_creator', 'ios', 'web'],
                    }
                }
            else:
                print("[INFO] Con cookies - dejando que yt-dlp elija los mejores clientes")
            
            opciones['http_headers']['Origin'] = 'https://www.youtube.com'
            opciones['http_headers']['Referer'] = 'https://www.youtube.com/'
            
        elif 'tiktok.com' in url_lower:
            opciones['http_headers']['Referer'] = 'https://www.tiktok.com/'
            opciones['http_headers']['Origin'] = 'https://www.tiktok.com'
            
        elif 'twitter.com' in url_lower or 'x.com' in url_lower:
            opciones['http_headers']['Referer'] = 'https://twitter.com/'
            opciones['http_headers']['Origin'] = 'https://twitter.com'
            
        elif 'facebook.com' in url_lower or 'fb.watch' in url_lower:
            opciones['http_headers']['Referer'] = 'https://www.facebook.com/'
            opciones['http_headers']['Origin'] = 'https://www.facebook.com'
            
        elif 'pornhub.com' in url_lower:
            opciones['http_headers']['Referer'] = 'https://www.pornhub.com/'
            opciones['http_headers']['Origin'] = 'https://www.pornhub.com'
            opciones['http_headers']['Age-Gate'] = '1'
            opciones['age_limit'] = 18
            if self.formato == "video":
                opciones['format'] = 'best[ext=mp4]/best'
        
        return opciones
    
    def construir_formato_video(self):
        """Construye la cadena de formato segun las opciones seleccionadas"""
        
        if 'pornhub.com' in self.url.lower():
            return 'best[ext=mp4]/best'
        
        resolucion = self.calidad.get('resolucion', 'Mejor disponible')
        fps = self.calidad.get('fps', 'Mejor disponible')
        audio_codec = self.calidad.get('audio_codec', 'Mejor disponible')
        audio_canales = self.calidad.get('audio_canales', 'Mejor disponible')
        
        video_filters = []
        
        if resolucion != "Mejor disponible":
            height_map = {
                "8K (4320p)": 4320,
                "5K (2880p)": 2880,
                "4K (2160p)": 2160,
                "2K (1440p)": 1440,
                "Full HD (1080p)": 1080,
                "HD (720p)": 720,
                "SD (480p)": 480,
                "360p": 360,
                "240p": 240,
                "144p": 144
            }
            height = height_map.get(resolucion, 0)
            if height > 0:
                video_filters.append(f"height<={height}")
        
        if fps == "60 FPS":
            video_filters.append("fps>=60")
        elif fps == "30 FPS":
            video_filters.append("fps<=30")
        
        audio_filters = []
        
        if audio_codec == "Opus (mejor calidad)":
            audio_filters.append("acodec=opus")
        elif audio_codec == "AAC (compatible)":
            audio_filters.append("acodec=aac")
        
        if audio_canales == "5.1 Surround":
            audio_filters.append("channels>=6")
        elif audio_canales == "Stereo":
            audio_filters.append("channels=2")
        
        if video_filters:
            video_selector = f"bv*[{']['.join(video_filters)}]"
        else:
            video_selector = "bv*"
        
        if audio_filters:
            audio_selector = f"ba*[{']['.join(audio_filters)}]"
        else:
            audio_selector = "ba*"
        
        formato = f"{video_selector}+{audio_selector}/{video_selector}+ba/bv*+{audio_selector}/bv*+ba/b"
        
        print(f"[DEBUG] Formato construido: {formato}")
        print(f"[DEBUG] Resolucion: {resolucion}")
        print(f"[DEBUG] FPS: {fps}")
        print(f"[DEBUG] Codec: {audio_codec}")
        print(f"[DEBUG] Canales: {audio_canales}")
        
        return formato
    
    def run(self):
        try:
            self.progreso.emit("Obteniendo informacion del video...")
            
            opciones = self.get_opciones_base()
            
            if self.config.get('limite_enabled', False):
                limite_bytes = self.config.get('limite_mbps', 10) * 125000
                opciones['ratelimit'] = limite_bytes
            
            def progress_hook(d):
                if d['status'] == 'downloading':
                    try:
                        percent = d.get('_percent_str', '0%')
                        speed = d.get('_speed_str', 'N/A')
                        eta = d.get('_eta_str', 'N/A')
                        self.progreso.emit(f"Descargando: {percent} | Velocidad: {speed} | Tiempo: {eta}")
                    except:
                        self.progreso.emit("Descargando...")
                elif d['status'] == 'finished':
                    self.progreso.emit("Procesando archivo...")
            
            opciones['progress_hooks'] = [progress_hook]
            
            if self.formato == "audio":
                opciones['format'] = 'bestaudio/best'
                opciones['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            else:
                formato_str = self.construir_formato_video()
                opciones['format'] = formato_str
                
                opciones['postprocessors'] = [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }, {
                    'key': 'FFmpegFixupM4a',
                }, {
                    'key': 'FFmpegFixupM3u8',
                }]
            
            opciones = self.configurar_plataforma(opciones)
            
            self.progreso.emit("Iniciando descarga...")
            
            print(f"[DEBUG] Formato final: {opciones.get('format')}")
            print(f"[DEBUG] URL: {self.url}")
            print(f"[DEBUG] Cookies: {opciones.get('cookiesfrombrowser', 'Archivo' if opciones.get('cookiefile') else 'No')}")
            print(f"[DEBUG] Clientes: {opciones.get('extractor_args', {}).get('youtube', {}).get('player_client', 'Por defecto')}")
            
            with yt_dlp.YoutubeDL(opciones) as ydl:
                info = ydl.extract_info(self.url, download=True)
                titulo = info.get('title', 'Video')
                self.completado.emit(titulo)
            
        except Exception as e:
            error_msg = str(e)
            print(f"[ERROR] {error_msg}")
            
            if '403' in error_msg or 'Forbidden' in error_msg:
                error_msg = (
                    "Error 403: Acceso denegado\n\n"
                    "Soluciones:\n"
                    "1. Actualiza yt-dlp: pip install --upgrade yt-dlp\n"
                    "2. Configura cookies del navegador en Configuracion\n"
                    "3. O exporta cookies.txt manualmente\n\n"
                    f"Error tecnico: {error_msg[:150]}"
                )
            elif '429' in error_msg:
                error_msg = "Demasiadas solicitudes\n\nEspera 5-10 minutos e intenta de nuevo"
            elif 'Sign in' in error_msg.lower() or 'login' in error_msg.lower():
                error_msg = "Video privado o requiere inicio de sesion\n\nNo se puede descargar"
            elif 'unavailable' in error_msg.lower():
                error_msg = "Video no disponible\n\nPuede haber sido eliminado o es privado"
            elif 'format' in error_msg.lower():
                error_msg = (
                    "Formato no disponible\n\n"
                    "Intenta:\n"
                    "- Cambiar la calidad\n"
                    "- Actualizar yt-dlp: pip install --upgrade yt-dlp\n"
                    "- Verificar que el video sea publico\n\n"
                    f"Error: {error_msg[:150]}"
                )
            else:
                error_msg = f"Error: {error_msg[:250]}"
            
            self.error.emit(error_msg)

class DescargadorVideos(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config_file = Path.home() / ".3ox_downloader_config.json"
        self.cargar_configuracion()
        self.descargando = False
        self.init_ui()
        self.aplicar_tema()

    def toggle_opciones_video(self):
        """Habilita/deshabilita opciones segun el tipo seleccionado"""
        es_video = self.video_radio.isChecked()
        
        for btn in self.resolucion_group.buttons():
            btn.setEnabled(es_video)
        
        for btn in self.fps_group.buttons():
            btn.setEnabled(es_video)
        
        for btn in self.audio_codec_group.buttons():
            btn.setEnabled(True)
        
        for btn in self.audio_canales_group.buttons():
            btn.setEnabled(True)
        
    def cargar_configuracion(self):
        self.config = {
            'hilos': 16,
            'ffmpeg_path': '',
            'limite_enabled': False,
            'limite_mbps': 10,
            'cookies_browser': 'Ninguno',
            'tema': 'Azul'
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
            except:
                pass
    
    def guardar_configuracion(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo guardar la configuracion: {e}")
    
    def get_tema_colores(self):
        temas = {
            'Azul': ('#89b4fa', '#74c7ec', '#5ea3d4'),
            'Rojo': ('#f38ba8', '#eba0ac', '#d47387'),
            'Amarillo': ('#f9e2af', '#f5e0a4', '#e6c77e'),
            'Verde': ('#a6e3a1', '#94d890', '#7fbf7a'),
            'Naranja': ('#fab387', '#f5a574', '#e68a5d'),
            'Morado': ('#cba6f7', '#b896e8', '#a37dd4'),
            'Rosa': ('#f5c2e7', '#ebadd6', '#d98fc4'),
            'Cafe': ('#b5a391', '#a69280', '#8f7d6f'),
            'Negro': ('#6c7086', '#585b70', '#45475a'),
            'Blanco': ('#cdd6f4', '#bac2de', '#a6adc8'),
            'Gris': ('#9399b2', '#7f849c', '#6c7086'),
            'Violeta': ('#b4befe', '#a5abed', '#8a92d8'),
            'Cian': ('#89dceb', '#74c7dd', '#5fb0c4'),
            'Magenta': ('#f5bde6', '#e9a9d6', '#d98fc4'),
            'Turquesa': ('#94e2d5', '#80d0c3', '#6bb8ac'),
            'Beige': ('#d9c8b0', '#c9b79d', '#b3a088'),
            'Plateado': ('#acb0be', '#999da8', '#838791'),
            'Dorado': ('#f5d061', '#eac24d', '#d4ab39'),
        }
        return temas.get(self.config.get('tema', 'Azul'), temas['Azul'])
    
    def aplicar_tema(self):
        color_primario, color_secundario, color_hover = self.get_tema_colores()

        self.setStyleSheet(f"""
    QMainWindow {{
        background-color: #1e1e2e;
    }}

    QLabel {{
        color: #cdd6f4;
    }}

    QLineEdit {{
        background-color: #313244;
        color: #cdd6f4;
        border: 2px solid #45475a;
        border-radius: 8px;
        padding: 12px;
        font-size: 13px;
        font-family: 'Segoe UI', Arial;
    }}

    QLineEdit:focus {{
        border: 2px solid {color_primario};
    }}

    QLineEdit:read-only {{
        background-color: #262637;
    }}

    QPushButton {{
        background-color: {color_secundario};
        color: #1e1e2e;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-size: 14px;
        font-weight: bold;
        font-family: 'Segoe UI', Arial;
    }}

    QPushButton:hover {{
        background-color: {color_primario};
    }}

    QPushButton:pressed {{
        background-color: {color_hover};
    }}

    QPushButton:disabled {{
        background-color: #45475a;
        color: #6c7086;
    }}

    QPushButton#small_btn {{
        background-color: #585b70;
        color: #cdd6f4;
        padding: 10px 20px;
        font-size: 12px;
    }}

    QPushButton#small_btn:hover {{
        background-color: #6c7086;
    }}

    QPushButton#config_btn {{
        background-color: #585b70;
        color: #cdd6f4;
        padding: 8px 16px;
        font-size: 11px;
    }}

    QPushButton#config_btn:hover {{
        background-color: {color_primario};
        color: #1e1e2e;
    }}

    QRadioButton {{
        color: #cdd6f4;
        font-size: 11px;
        font-family: 'Segoe UI', Arial;
        spacing: 8px;
        padding: 5px;
    }}

    QRadioButton::indicator {{
        width: 16px;
        height: 16px;
        border-radius: 8px;
        border: 2px solid #6c7086;
        background-color: transparent;
    }}

    QRadioButton::indicator:hover {{
        border: 2px solid {color_secundario};
    }}

    QRadioButton::indicator:checked {{
        background-color: {color_primario};
        border: 2px solid {color_primario};
    }}

    QRadioButton:disabled {{
        color: #6c7086;
    }}

    QRadioButton::indicator:disabled {{
        border: 2px solid #45475a;
        background-color: transparent;
    }}

    QComboBox {{
        background-color: #313244;
        color: #cdd6f4;
        border: 2px solid #45475a;
        border-radius: 8px;
        padding: 10px 15px;
        font-size: 11px;
        font-family: 'Segoe UI', Arial;
    }}

    QComboBox:focus {{
        border: 2px solid {color_primario};
    }}

    QComboBox:disabled {{
        background-color: #262637;
        color: #6c7086;
    }}

    QComboBox::drop-down {{
        border: none;
        width: 30px;
        padding-right: 5px;
    }}

    QComboBox::down-arrow {{
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 6px solid #cdd6f4;
        margin-right: 8px;
    }}

    QComboBox::down-arrow:disabled {{
        border-top: 6px solid #6c7086;
    }}

    QComboBox QAbstractItemView {{
        background-color: #313244;
        color: #cdd6f4;
        border: 2px solid #45475a;
        border-radius: 8px;
        outline: none;
    }}

    QComboBox QAbstractItemView::item {{
        padding: 6px 10px;
    }}

    QComboBox QAbstractItemView::item:selected {{
        background-color: rgba(137, 180, 250, 0.25);
    }}

    QProgressBar {{
        background-color: #313244;
        border: none;
        border-radius: 8px;
        height: 28px;
        text-align: center;
        font-family: 'Segoe UI', Arial;
        font-size: 12px;
        color: #cdd6f4;
    }}

    QProgressBar::chunk {{
        background-color: {color_primario};
        border-radius: 8px;
    }}

    QGroupBox {{
        background-color: #181825;
        border-radius: 12px;
        border: 1px solid #313244;
        margin-top: 12px;
        padding-top: 15px;
        font-family: 'Segoe UI', Arial;
    }}

    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 5px 10px;
        color: {color_primario};
        font-size: 13px;
        font-weight: bold;
    }}

    QScrollArea {{
        border: none;
        background-color: transparent;
    }}

    QScrollBar:vertical {{
        background: #313244;
        width: 12px;
        border-radius: 6px;
    }}

    QScrollBar::handle:vertical {{
        background: #585b70;
        border-radius: 6px;
        min-height: 20px;
    }}

    QScrollBar::handle:vertical:hover {{
        background: #6c7086;
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
        """)
        
    def init_ui(self):
        self.setWindowTitle("3oX Downloader")
        self.setFixedSize(850, 950)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(18)

        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #313244; border-radius: 12px;")
        header_frame.setFixedHeight(100)
        header_layout = QVBoxLayout(header_frame)
        header_layout.setAlignment(Qt.AlignCenter)
        
        title = QLabel("3oX DOWNLOADER")
        title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title)
        
        subtitle = QLabel("YouTube - TikTok - Twitter - Facebook")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: #a6adc8;")
        subtitle.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(subtitle)
        
        main_layout.addWidget(header_frame)
        
        url_group = DiagonalGroupBox("URL del Video")
        url_layout = QVBoxLayout()
        url_layout.setContentsMargins(15, 15, 15, 15)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Ingresa la URL del video aqui...")
        self.url_input.setFont(QFont("Segoe UI", 12))
        url_layout.addWidget(self.url_input)
        
        url_group.setLayout(url_layout)
        main_layout.addWidget(url_group)
        
        opciones_group = DiagonalGroupBox("Opciones de Descarga")
        opciones_group.setFixedHeight(290)
        opciones_container = QVBoxLayout()
        opciones_container.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:vertical {
                background: rgba(30, 30, 46, 0.5);
                width: 8px;
                margin: 2px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: rgba(69, 71, 90, 0.8);
                border-radius: 4px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(88, 91, 112, 1);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)
        
        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background: transparent;")
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(10)
        scroll_layout.setContentsMargins(20, 15, 15, 18)
        
        tipo_layout = QHBoxLayout()
        tipo_label = QLabel("Tipo:")
        tipo_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        tipo_label.setFixedWidth(110)
        tipo_layout.addWidget(tipo_label)
        
        self.tipo_group = QButtonGroup()
        
        self.video_radio = QRadioButton("Video completo")
        self.video_radio.setFont(QFont("Segoe UI", 10))
        self.video_radio.setChecked(True)
        self.video_radio.toggled.connect(self.toggle_opciones_video)
        self.tipo_group.addButton(self.video_radio)
        tipo_layout.addWidget(self.video_radio)
        
        self.audio_radio = QRadioButton("Solo audio (MP3)")
        self.audio_radio.setFont(QFont("Segoe UI", 10))
        self.audio_radio.toggled.connect(self.toggle_opciones_video)
        self.tipo_group.addButton(self.audio_radio)
        tipo_layout.addWidget(self.audio_radio)
        
        tipo_layout.addStretch()
        scroll_layout.addLayout(tipo_layout)
        
        res_layout = QHBoxLayout()
        res_layout.setAlignment(Qt.AlignTop)
        res_label = QLabel("Resolucion:")
        res_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        res_label.setFixedWidth(110)
        res_label.setAlignment(Qt.AlignTop)
        res_layout.addWidget(res_label)
        
        self.resolucion_group = QButtonGroup()
        res_container = QVBoxLayout()
        res_container.setSpacing(6)
        res_container.setContentsMargins(0, 0, 0, 0)
        
        res_row1 = QHBoxLayout()
        res_row1.setSpacing(8)
        for opcion in ["Mejor disponible", "8K (4320p)", "4K (2160p)", "2K (1440p)"]:
            rb = QRadioButton(opcion)
            rb.setFont(QFont("Segoe UI", 9))
            if opcion == "Mejor disponible":
                rb.setChecked(True)
            self.resolucion_group.addButton(rb)
            res_row1.addWidget(rb)
        res_row1.addStretch()
        res_container.addLayout(res_row1)
        
        res_row2 = QHBoxLayout()
        res_row2.setSpacing(8)
        for opcion in ["Full HD (1080p)", "HD (720p)", "SD (480p)", "360p"]:
            rb = QRadioButton(opcion)
            rb.setFont(QFont("Segoe UI", 9))
            self.resolucion_group.addButton(rb)
            res_row2.addWidget(rb)
        res_row2.addStretch()
        res_container.addLayout(res_row2)
        
        res_layout.addLayout(res_container)
        scroll_layout.addLayout(res_layout)
        
        fps_layout = QHBoxLayout()
        fps_label = QLabel("FPS:")
        fps_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        fps_label.setFixedWidth(110)
        fps_layout.addWidget(fps_label)
        
        self.fps_group = QButtonGroup()
        for opcion in ["Mejor disponible", "60 FPS", "30 FPS"]:
            rb = QRadioButton(opcion)
            rb.setFont(QFont("Segoe UI", 9))
            if opcion == "Mejor disponible":
                rb.setChecked(True)
            self.fps_group.addButton(rb)
            fps_layout.addWidget(rb)
        fps_layout.addStretch()
        scroll_layout.addLayout(fps_layout)
        
        codec_layout = QHBoxLayout()
        codec_label = QLabel("Codec Audio:")
        codec_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        codec_label.setFixedWidth(110)
        codec_layout.addWidget(codec_label)
        
        self.audio_codec_group = QButtonGroup()
        for opcion in ["Mejor disponible", "Opus (mejor calidad)", "AAC (compatible)"]:
            rb = QRadioButton(opcion)
            rb.setFont(QFont("Segoe UI", 9))
            if opcion == "Mejor disponible":
                rb.setChecked(True)
            self.audio_codec_group.addButton(rb)
            codec_layout.addWidget(rb)
        codec_layout.addStretch()
        scroll_layout.addLayout(codec_layout)
        
        canales_layout = QHBoxLayout()
        canales_label = QLabel("Canales:")
        canales_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        canales_label.setFixedWidth(110)
        canales_layout.addWidget(canales_label)
        
        self.audio_canales_group = QButtonGroup()
        for opcion in ["Mejor disponible", "5.1 Surround", "Stereo"]:
            rb = QRadioButton(opcion)
            rb.setFont(QFont("Segoe UI", 9))
            if opcion == "Mejor disponible":
                rb.setChecked(True)
            self.audio_canales_group.addButton(rb)
            canales_layout.addWidget(rb)
        canales_layout.addStretch()
        scroll_layout.addLayout(canales_layout)
        
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_widget)
        opciones_container.addWidget(scroll)
        opciones_group.setLayout(opciones_container)
        main_layout.addWidget(opciones_group)
        
        carpeta_group = DiagonalGroupBox("Carpeta de Destino")
        carpeta_layout = QHBoxLayout()
        carpeta_layout.setContentsMargins(15, 15, 15, 15)
        
        self.carpeta_input = QLineEdit()
        self.carpeta_input.setText(str(Path.home() / "Downloads" / "Videos"))
        self.carpeta_input.setFont(QFont("Segoe UI", 11))
        carpeta_layout.addWidget(self.carpeta_input)
        
        examinar_btn = QPushButton("Examinar")
        examinar_btn.setObjectName("small_btn")
        examinar_btn.setFixedWidth(140)
        examinar_btn.clicked.connect(self.seleccionar_carpeta)
        carpeta_layout.addWidget(examinar_btn)
        
        carpeta_group.setLayout(carpeta_layout)
        main_layout.addWidget(carpeta_group)
        
        config_btn = QPushButton("Configuracion")
        config_btn.setObjectName("small_btn")
        config_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        config_btn.setFixedHeight(50)
        config_btn.clicked.connect(self.abrir_configuracion)
        main_layout.addWidget(config_btn)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setFont(QFont("Segoe UI", 10))
        main_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("")
        self.status_label.setFont(QFont("Segoe UI", 10))
        self.status_label.setStyleSheet("color: #a6adc8;")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setWordWrap(True)
        main_layout.addWidget(self.status_label)
        
        self.descargar_btn = QPushButton("DESCARGAR")
        self.descargar_btn.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.descargar_btn.setFixedHeight(55)
        self.descargar_btn.clicked.connect(self.iniciar_descarga)
        main_layout.addWidget(self.descargar_btn)
        
        footer = QLabel("Powered by yt-dlp and developed by Agente 308")
        footer.setFont(QFont("Segoe UI", 9))
        footer.setStyleSheet("color: #6c7086;")
        footer.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(footer)
    
    def get_selected_radio_text(self, button_group):
        """Obtiene el texto del RadioButton seleccionado"""
        checked_button = button_group.checkedButton()
        if checked_button:
            return checked_button.text()
        return "Mejor disponible"
    
    def abrir_configuracion(self):
        dialog = ConfigDialog(self)
        dialog.exec_()
        
    def seleccionar_carpeta(self):
        carpeta = QFileDialog.getExistingDirectory(
            self, "Seleccionar Carpeta", self.carpeta_input.text()
        )
        if carpeta:
            self.carpeta_input.setText(carpeta)
    
    def iniciar_descarga(self):
        if self.descargando:
            QMessageBox.warning(self, "Descarga en progreso", 
                              "Ya hay una descarga en curso. Por favor espera.")
            return
        
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.critical(self, "Error", "Por favor ingresa una URL valida.")
            return
        
        carpeta = self.carpeta_input.text()
        if not os.path.exists(carpeta):
            os.makedirs(carpeta)
        
        formato = "audio" if self.audio_radio.isChecked() else "video"
        
        opciones_calidad = {
            'resolucion': self.get_selected_radio_text(self.resolucion_group),
            'fps': self.get_selected_radio_text(self.fps_group),
            'audio_codec': self.get_selected_radio_text(self.audio_codec_group),
            'audio_canales': self.get_selected_radio_text(self.audio_canales_group)
        }
        
        self.descargando = True
        self.descargar_btn.setEnabled(False)
        self.progress_bar.setMaximum(0)
        self.progress_bar.setValue(0)
        
        self.thread = DescargadorThread(url, carpeta, formato, opciones_calidad, self.config)
        self.thread.progreso.connect(self.actualizar_progreso)
        self.thread.completado.connect(self.descarga_completada)
        self.thread.error.connect(self.descarga_fallida)
        self.thread.start()
    
    def actualizar_progreso(self, mensaje):
        self.status_label.setText(mensaje)
    
    def descarga_completada(self, titulo):
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(100)
        self.descargando = False
        self.descargar_btn.setEnabled(True)
        self.status_label.setText("Descarga completada exitosamente")
        
        QMessageBox.information(
            self, "Descarga completada",
            f"Video descargado exitosamente!\n\n{titulo}\n\nUbicacion: {self.carpeta_input.text()}"
        )
        
        self.url_input.clear()
        self.progress_bar.setValue(0)
        self.status_label.setText("")
    
    def descarga_fallida(self, error):
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.descargando = False
        self.descargar_btn.setEnabled(True)
        self.status_label.setText("Error en la descarga")
        
        QMessageBox.critical(
            self, "Error",
            f"No se pudo descargar el video.\n\n{error}"
        )

def main():
    app = QApplication(sys.argv)
    ventana = DescargadorVideos()
    ventana.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()