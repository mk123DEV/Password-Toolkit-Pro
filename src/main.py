# src/main.py

import sys
import pyperclip
import time
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QTimer, QRunnable, QThreadPool, QObject, Signal

# On importe nos propres modules
from ui.main_window import MainWindowUI
import core_logic

# --- Étape 1: Créer un "Worker" qui peut s'exécuter sur un autre thread ---

class WorkerSignals(QObject):
    """Définit les signaux disponibles pour un worker."""
    result = Signal(int) # Signal qui transportera le résultat (un entier : pwned_count)

class PwnedAPIChecker(QRunnable):
    """
    Worker qui exécute la vérification sur l'API HIBP dans un thread séparé.
    """
    def __init__(self, password):
        super().__init__()
        self.password = password
        self.signals = WorkerSignals()

    def run(self):
        """La logique qui s'exécute sur le thread secondaire."""
        count = core_logic.verifier_mot_de_passe_pwned(self.password)
        self.signals.result.emit(count) # On émet le signal avec le résultat

# --- Classe principale de l'application ---

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("assets/icon.ico"))
        self.ui = MainWindowUI()
        self.ui.setup_ui(self)
        
        # Le QThreadPool gère notre pool de threads
        self.thread_pool = QThreadPool()

        # Le timer est toujours utile pour le "debouncing"
        self.analysis_timer = QTimer(self)
        self.analysis_timer.setSingleShot(True)
        self.analysis_timer.setInterval(500) # 500ms
        self.analysis_timer.timeout.connect(self.trigger_password_analysis)

        self._connect_signals()
        self.update_password_length_label()
        self.generate_password()

    def _connect_signals(self):
        self.ui.longueurSlider.valueChanged.connect(self.update_password_length_label)
        self.ui.genererButton.clicked.connect(self.generate_password)
        self.ui.copierButton.clicked.connect(self.copy_to_clipboard)
        self.ui.analyseLineEdit.textChanged.connect(self.analysis_timer.start) # La frappe redémarre le timer

    # --- Fonctions de logique ---

    def trigger_password_analysis(self):
        """
        Déclenche l'analyse locale (rapide) et lance le worker pour l'analyse en ligne (lente).
        """
        password = self.ui.analyseLineEdit.text()
        
        # 1. On fait l'analyse locale immédiatement, car elle est rapide
        analyse_locale = core_logic.analyser_force_mot_de_passe(password)
        self.update_ui_with_local_analysis(analyse_locale)

        # 2. On crée et lance le worker pour la tâche lente
        worker = PwnedAPIChecker(password)
        worker.signals.result.connect(self.update_ui_with_pwned_result) # On connecte le signal du worker
        self.thread_pool.start(worker) # On donne le worker au QThreadPool pour exécution

    def update_ui_with_local_analysis(self, analyse_locale):
        """Met à jour l'UI avec les résultats de l'analyse zxcvbn (rapide)."""
        score = analyse_locale['score']
        self.ui.forceProgressBar.setValue(score)

        if score <= 1: color, force_text = "#ff4d4d", "Très Faible"
        elif score == 2: color, force_text = "#ffcc00", "Faible"
        elif score == 3: color, force_text = "#99cc33", "Moyen"
        else: color, force_text = "#66cc66", "Fort"
        
        self.ui.forceLabel.setText(f"Force : {force_text}")
        self.ui.forceProgressBar.setStyleSheet(f"QProgressBar::chunk {{ background-color: {color}; }}")
        self.ui.tempsCrackLabel.setText(f"Temps de cassage estimé : {analyse_locale['temps_crack_affichage']}")

        # On nettoie le feedback en attendant le résultat de l'API
        feedback_lines = []
        if analyse_locale['avertissements']:
            feedback_lines.append("AVERTISSEMENTS LOCAUX :\n" + "\n".join(f"- {a}" for a in analyse_locale['avertissements']))
        if analyse_locale['suggestions']:
            feedback_lines.append("SUGGESTIONS :\n" + "\n".join(f"- {s}" for s in analyse_locale['suggestions']))
        
        final_feedback = "\n\n".join(feedback_lines)
        if not final_feedback and self.ui.analyseLineEdit.text():
             final_feedback = "Analyse en ligne en cours..."
        self.ui.feedbackTextEdit.setText(final_feedback)

    def update_ui_with_pwned_result(self, pwned_count):
        """
        Met à jour l'UI une fois que le worker a terminé et renvoyé le résultat.
        """
        if pwned_count > 0:
            self.ui.forceLabel.setText("Force : COMPROMIS !")
            self.ui.forceProgressBar.setValue(0)
            self.ui.forceProgressBar.setStyleSheet(f"QProgressBar::chunk {{ background-color: #ff0000; }}")
            
            current_text = self.ui.feedbackTextEdit.toPlainText()
            pwned_warning = f"!!! ATTENTION !!!\nCe mot de passe a été trouvé {pwned_count:,} fois dans des fuites de données. Ne l'utilisez JAMAIS."
            self.ui.feedbackTextEdit.setText(pwned_warning + "\n\n" + current_text)
        elif pwned_count == -1:
            current_text = self.ui.feedbackTextEdit.toPlainText()
            error_warning = "AVERTISSEMENT : Impossible de vérifier si le mot de passe a été compromis (erreur réseau)."
            self.ui.feedbackTextEdit.setText(error_warning + "\n\n" + current_text)
        else: # pwned_count == 0
            if "Analyse en ligne en cours..." in self.ui.feedbackTextEdit.toPlainText():
                self.ui.feedbackTextEdit.setText("Aucune faiblesse évidente détectée. Ce mot de passe semble robuste.")


    def update_password_length_label(self):
        longueur = self.ui.longueurSlider.value()
        self.ui.longueurLabel.setText(f"Longueur : {longueur}")

    def generate_password(self):
        longueur = self.ui.longueurSlider.value()
        inclure_majuscules = self.ui.majusculesCheckBox.isChecked()
        inclure_nombres = self.ui.nombresCheckBox.isChecked()
        inclure_symboles = self.ui.symbolesCheckBox.isChecked()
        password = core_logic.generer_mot_de_passe(longueur, inclure_majuscules, inclure_nombres, inclure_symboles)
        self.ui.mdpGenereLineEdit.setText(password)
        self.ui.analyseLineEdit.setText(password)

    def copy_to_clipboard(self):
        password = self.ui.mdpGenereLineEdit.text()
        if not password: return
        pyperclip.copy(password)
        original_text = self.ui.copierButton.text()
        self.ui.copierButton.setText("Copié !")
        self.ui.copierButton.repaint()
        QApplication.processEvents()
        time.sleep(0.8)
        self.ui.copierButton.setText(original_text)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()