# src/ui/main_window.py

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QGroupBox, QLabel, QLineEdit, QSlider, QCheckBox, QPushButton,
    QProgressBar, QTextEdit
)
from PySide6.QtCore import Qt

class MainWindowUI:

    def setup_ui(self, main_window: QMainWindow):
        # --- Configuration de la fenêtre principale ---
        main_window.setWindowTitle("Password Toolkit Pro")
        main_window.setMinimumSize(800, 550)

        # --- Création du widget central et du layout principal (Horizontal) ---
        central_widget = QWidget()
        main_window.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # --- Création des deux sections ---
        generator_groupbox = self.create_generator_groupbox()
        analyzer_groupbox = self.create_analyzer_groupbox()

        # --- Ajout des deux sections au layout principal ---
        main_layout.addWidget(generator_groupbox)
        main_layout.addWidget(analyzer_groupbox)

    def create_generator_groupbox(self) -> QGroupBox:
      
        groupbox = QGroupBox("Générateur de Mot de Passe")
        layout = QVBoxLayout() # Layout vertical pour empiler les widgets
        
        # Création des widgets
        self.mdpGenereLineEdit = QLineEdit()
        self.mdpGenereLineEdit.setPlaceholderText("Votre mot de passe sécurisé...")
        
        self.longueurLabel = QLabel("Longueur : 16")
        
        self.longueurSlider = QSlider(Qt.Orientation.Horizontal)
        self.longueurSlider.setRange(8, 64)
        self.longueurSlider.setValue(16)
        
        self.majusculesCheckBox = QCheckBox("Inclure des majuscules (A-Z)")
        self.majusculesCheckBox.setChecked(True)
        
        self.nombresCheckBox = QCheckBox("Inclure des nombres (0-9)")
        self.nombresCheckBox.setChecked(True)
        
        self.symbolesCheckBox = QCheckBox("Inclure des symboles (!@#$%)")
        self.symbolesCheckBox.setChecked(True)

        self.copierButton = QPushButton("Copier")
        self.genererButton = QPushButton("Générer un Mot de Passe")

        # Ajout des widgets au layout de cette section
        layout.addWidget(self.mdpGenereLineEdit)
        layout.addWidget(self.longueurLabel)
        layout.addWidget(self.longueurSlider)
        layout.addWidget(self.majusculesCheckBox)
        layout.addWidget(self.nombresCheckBox)
        layout.addWidget(self.symbolesCheckBox)
        layout.addStretch()  # Ajoute un espace flexible pour pousser les boutons vers le bas
        layout.addWidget(self.copierButton)
        layout.addWidget(self.genererButton)
        
        groupbox.setLayout(layout)
        return groupbox

    def create_analyzer_groupbox(self) -> QGroupBox:
        """Crée la section 'Analyseur de Force'."""
        groupbox = QGroupBox("Analyseur de Force")
        layout = QVBoxLayout()
        
        # Création des widgets
        self.analyseLineEdit = QLineEdit()
        self.analyseLineEdit.setPlaceholderText("Tapez un mot de passe à analyser...")
        
        self.forceProgressBar = QProgressBar()
        self.forceProgressBar.setRange(0, 4) # Le score zxcvbn va de 0 à 4
        self.forceProgressBar.setValue(0)
        self.forceProgressBar.setTextVisible(False)
        
        self.forceLabel = QLabel("Force : N/A")
        self.tempsCrackLabel = QLabel("Temps de cassage estimé : N/A")
        
        self.feedbackTextEdit = QTextEdit()
        self.feedbackTextEdit.setReadOnly(True)

        # Ajout des widgets au layout de cette section
        layout.addWidget(self.analyseLineEdit)
        layout.addWidget(self.forceProgressBar)
        layout.addWidget(self.forceLabel)
        layout.addWidget(self.tempsCrackLabel)
        layout.addWidget(self.feedbackTextEdit)

        groupbox.setLayout(layout)
        return groupbox
