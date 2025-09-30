#!/usr/bin/env python3
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QSlider,
    QHBoxLayout, QPushButton, QSystemTrayIcon, QMenu, QAction
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QPixmap, QColor, QPalette, QBrush
import pulsectl

class VolumeControlApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("mexe ai fdppp")
        self.setGeometry(100, 100, 400, 300)
        self.setMinimumSize(300, 200)

        try:
            self.pulse = pulsectl.Pulse('volume-control-app')
        except Exception as e:
            print(f"Erro ao conectar com PulseAudio: {e}")
            sys.exit(1)

        # Configuração visual
        self.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 8px;
                background: #555555;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                width: 16px;
                margin: -4px 0;
                background: #aaaaaa;
                border-radius: 8px;
            }
            QPushButton {
                background: #555555;
                padding: 5px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: #666666;
            }
        """)

        # Configura o fundo com a imagem local
        self.set_background_image("wpp.png")
        
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(10)
        self.setLayout(self.layout)

        self.init_tray_icon()
        self.create_update_button()

        self.streams_container = QWidget()
        self.streams_layout = QVBoxLayout()
        self.streams_layout.setSpacing(8)
        self.streams_container.setLayout(self.streams_layout)
        self.layout.addWidget(self.streams_container)

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_streams)
        self.update_timer.start(5000)

        self.update_streams()

    def set_background_image(self, image_path):
        self.setAutoFillBackground(True)
        palette = self.palette()
        try:
            pixmap = QPixmap(image_path)
            palette.setBrush(self.backgroundRole(), 
                           QBrush(pixmap.scaled(
                               self.size(), 
                               Qt.IgnoreAspectRatio, 
                               Qt.SmoothTransformation)))
            self.setPalette(palette)
        except Exception as e:
            print(f"Erro ao carregar imagem de fundo: {e}")
            palette.setColor(self.backgroundRole(), QColor(40, 40, 40))
            self.setPalette(palette)

    def resizeEvent(self, event):
        self.set_background_image("wpp.png")
        super().resizeEvent(event)

    def init_tray_icon(self):
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)
            try:
                self.tray_icon.setIcon(QIcon("wpp.png"))
            except:
                self.tray_icon.setIcon(QIcon.fromTheme("audio-volume-high"))

            tray_menu = QMenu()
            
            show_action = QAction("Mostrar Controles", self)
            show_action.triggered.connect(self.show_normal)
            tray_menu.addAction(show_action)
            
            refresh_action = QAction("Atualizar Aplicativos", self)
            refresh_action.triggered.connect(self.update_streams)
            tray_menu.addAction(refresh_action)
            
            tray_menu.addSeparator()
            
            quit_action = QAction("Sair da Discoteca", self)
            quit_action.triggered.connect(self.close_app)
            tray_menu.addAction(quit_action)

            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()
            
            # Mostra notificação inicial
            self.tray_icon.showMessage(
                "Discoteca dos Cria",
                "Controle de volume iniciado!",
                QSystemTrayIcon.Information,
                2000
            )

    def show_normal(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def create_update_button(self):
        refresh_button = QPushButton("f5zada")
        refresh_button.setCursor(Qt.PointingHandCursor)
        refresh_button.clicked.connect(self.update_streams)
        # Estilo específico para o botão f5zada
        refresh_button.setStyleSheet("""
            QPushButton {
                background: white;
                color: black;
                font-weight: bold;
                border: 1px solid #ccc;
            }
            QPushButton:hover {
                background: #f0f0f0;
            }
        """)
        self.layout.addWidget(refresh_button)

    def update_streams(self):
        try:
            # Mapeamento de nomes personalizados
            name_mapping = {
                'firefox': 'firefox bebel',
                'spotify': 'spotify bebel',
                'WEBRTC VoiceEngine': 'discord bebel',
                'vlc': 'VLC Player',
                'chrome': 'chrome bebel',
                'google-chrome': 'chrome bebel',
                'teams': 'Microsoft Teams',
                'zoom': 'Zoom',
                'obs': 'OBS Studio',
                'plex': 'Plex Media',
                'steam': 'Steam',
                'whatsapp': 'zap bebel',
                'signal': 'Signal',
                'thunderbird': 'E-mail',
                'slack': 'Slack'
            }

            # Lista de processos para ignorar
            ignore_processes = ['speech-dispatcher-dummy']

            # Limpa os widgets antigos
            while self.streams_layout.count():
                item = self.streams_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()

            sink_inputs = self.pulse.sink_input_list()
            if not sink_inputs:
                label = QLabel("🎵 Nenhum aplicativo de áudio ativo no momento")
                label.setAlignment(Qt.AlignCenter)
                label.setStyleSheet("color: white;")
                self.streams_layout.addWidget(label)
                return

            for sink_input in sink_inputs:
                app_name = sink_input.proplist.get('application.name', 'Aplicativo Desconhecido')
                
                # Ignora processos na lista de ignore
                if app_name in ignore_processes:
                    continue
                
                # Aplica o mapeamento de nomes
                display_name = name_mapping.get(app_name, name_mapping.get(app_name.lower(), app_name))
                display_text = f"🔊 {display_name}"

                volume_percent = int(self.pulse.volume_get_all_chans(sink_input) * 100)

                h_layout = QHBoxLayout()
                label = QLabel(display_text)
                label.setMinimumWidth(150)
                label.setStyleSheet("color: white;")
                
                slider = QSlider(Qt.Horizontal)
                slider.setMinimum(0)
                slider.setMaximum(150)
                slider.setValue(volume_percent)
                slider.valueChanged.connect(lambda val, s=sink_input: self.change_volume(s, val))
                slider.setStyleSheet("""
                    QSlider::sub-page:horizontal {
                        background: #4CAF50;
                    }
                """)

                h_layout.addWidget(label)
                h_layout.addWidget(slider)

                container = QWidget()
                container.setLayout(h_layout)
                self.streams_container.layout().addWidget(container)

        except Exception as e:
            print(f"Erro ao atualizar streams: {e}")

    def change_volume(self, sink_input, value):
        try:
            volume = pulsectl.PulseVolumeInfo([value / 100.0] * len(sink_input.volume.values))
            self.pulse.sink_input_volume_set(sink_input.index, volume)
        except Exception as e:
            print(f"Erro ao alterar volume: {e}")

    def close_app(self):
        try:
            self.pulse.close()
        except:
            pass
        QApplication.quit()

    def closeEvent(self, event):
        if hasattr(self, 'tray_icon') and self.tray_icon.isVisible():
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "Discoteca dos Cria",
                "O controle foi minimizado para a bandeja",
                QSystemTrayIcon.Information,
                2000
            )
        else:
            self.close_app()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setStyle('Fusion')  # Melhora a aparência no Linux
    
    # Configura para evitar problemas com threads
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    window = VolumeControlApp()
    window.show()
    sys.exit(app.exec_())