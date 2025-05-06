from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import argparse
from dotenv import load_dotenv

class DoctolibScraper:
    def __init__(self):
        self.setup_driver()
        
    def setup_driver(self):
        """Configuration du driver Selenium"""
        try:
            # Configuration des options Chrome
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Vérifier les chemins possibles de Chrome
            possible_chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Google Chrome.lnk"
            ]
            
            chrome_path = None
            for path in possible_chrome_paths:
                if os.path.exists(path):
                    chrome_path = path
                    print(f"Chrome trouvé à : {path}")
                    break
            
            if chrome_path:
                if chrome_path.endswith('.lnk'):
                    print("ATTENTION : Un raccourci Chrome a été trouvé, ce n'est pas l'exécutable")
                else:
                    chrome_options.binary_location = chrome_path
                    print(f"Utilisation de Chrome à : {chrome_path}")
            else:
                print("Chrome n'a pas été trouvé dans les emplacements standards")
            
            # Installation et configuration du ChromeDriver
            print("Installation du ChromeDriver...")
            driver_path = ChromeDriverManager().install()
            print(f"ChromeDriver installé à : {driver_path}")
            
            service = Service(executable_path=driver_path)
            
            # Création du driver avec les options et le service
            print("Lancement de Chrome...")
            self.driver = webdriver.Chrome(
                service=service,
                options=chrome_options
            )
            
            # Configuration de l'user agent
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
            })
            
            print("Chrome a été lancé avec succès")
            
        except Exception as e:
            print(f"Erreur lors du lancement de Chrome : {str(e)}")
            print("Tentative de lancement avec une configuration alternative...")
            
            try:
                # Configuration alternative
                chrome_options = Options()
                chrome_options.add_argument("--start-maximized")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--disable-blink-features=AutomationControlled")
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_experimental_option('useAutomationExtension', False)
                
                # Utiliser le chemin direct vers Chrome
                if chrome_path and not chrome_path.endswith('.lnk'):
                    chrome_options.binary_location = chrome_path
                    print(f"Utilisation de Chrome à : {chrome_path}")
                
                # Création du driver avec les options
                print("Lancement de Chrome avec la configuration alternative...")
                self.driver = webdriver.Chrome(options=chrome_options)
                
                # Configuration de l'user agent
                self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                    "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
                })
                
                print("Chrome a été lancé avec succès en utilisant la configuration alternative")
                
            except Exception as e:
                print(f"Erreur lors de la tentative alternative : {str(e)}")
                raise

    def extract_doctor_info(self, doctor_card):
        """Extrait les informations d'un médecin depuis sa carte"""
        try:
            # Récupérer le nom du praticien
            name_element = doctor_card.find_element(By.CSS_SELECTOR, "span[itemprop='name']")
            doctor_name = name_element.text
            print(f"Nom du praticien : {doctor_name}")
            
            # Cliquer sur le bouton "Prendre rendez-vous"
            appointment_button = doctor_card.find_element(By.CSS_SELECTOR, "button.dl-button-primary span.dl-button-label")
            if appointment_button.text == "Prendre rendez-vous":
                appointment_button.click()
                time.sleep(2)  # Attendre que la page se charge
                
                # Attendre que l'élément de conventionnement soit présent
                wait = WebDriverWait(self.driver, 10)
                convention_element = wait.until(
                    EC.presence_of_element_located((
                        By.CSS_SELECTOR,
                        "p.dl-text.dl-text-body.dl-text-regular.dl-text-s.dl-text-neutral-130"
                    ))
                )
                
                # Récupérer le statut de conventionnement
                convention_status = convention_element.text
                
                # Retourner à la page précédente
                self.driver.back()
                time.sleep(2)  # Attendre que la page se recharge
                
                return convention_status
            else:
                print("Bouton 'Prendre rendez-vous' non trouvé")
                return "Information non disponible"
            
        except Exception as e:
            print(f"Erreur lors de l'extraction des informations : {str(e)}")
            # Retourner à la page précédente en cas d'erreur
            try:
                self.driver.back()
                time.sleep(2)
            except:
                pass
            return "Information non disponible"

    def search_doctors(self, postal_code, specialty):
        """Recherche de médecins par code postal et spécialité"""
        try:
            print("Accès au site Doctolib...")
            self.driver.get("https://www.doctolib.fr")
            time.sleep(5)  # Attendre que la page se charge complètement
            
            # Accepter les cookies si nécessaire
            try:
                cookie_button = WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "button#didomi-notice-agree-button"))
                )
                cookie_button.click()
                time.sleep(2)
            except Exception as e:
                print(f"Pas de popup de cookies ou erreur : {str(e)}")

            # Attendre que les champs de recherche soient présents
            wait = WebDriverWait(self.driver, 20)
            
            # Recherche par spécialité
            print(f"Recherche de la spécialité : {specialty}")
            query_input = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                    "input.searchbar-input.searchbar-query-input")))
            
            # Effacer le champ et saisir la spécialité
            query_input.clear()
            query_input.send_keys(specialty)
            time.sleep(2)
            query_input.send_keys(Keys.ENTER)
            
            # Attendre que la spécialité soit bien saisie
            wait.until(
                EC.text_to_be_present_in_element_value((By.CSS_SELECTOR,
                    "input.searchbar-input.searchbar-query-input"),
                    specialty))
            
            # Valider la recherche
            query_input.send_keys(Keys.ENTER)
            time.sleep(3)

            # Recherche par code postal
            print(f"Recherche du code postal : {postal_code}")
            place_input = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                    "input.searchbar-input.searchbar-place-input")))
            
            # Effacer le champ et saisir le code postal
            place_input.clear()
            place_input.send_keys(postal_code)
            
            # Attendre que le code postal soit bien saisi
            wait.until(
                EC.text_to_be_present_in_element_value((By.CSS_SELECTOR,
                    "input.searchbar-input.searchbar-place-input"),
                    postal_code))
            
            # Valider la recherche
            place_input.send_keys(Keys.ENTER)

            # Attendre et afficher le nombre de résultats
            total_results = wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR,
                "div[data-test='total-number-of-results']"
            )))
            print("Nombre de résultats trouvés : ", total_results.text)
            
            # Compter le nombre de boutons "Prendre rendez-vous"
            appointment_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                "button.dl-button-primary span.dl-button-label")
            appointment_count = sum(1 for button in appointment_buttons if button.text == "Prendre rendez-vous")
            print(f"Nombre de boutons 'Prendre rendez-vous' trouvés : {appointment_count}")
            
            # Attendre que les cartes des médecins soient chargées
            time.sleep(3)
            
            # Récupérer les 10 premières cartes de médecins
            doctor_cards = wait.until(
                EC.presence_of_all_elements_located((
                    By.CSS_SELECTOR,
                    "div.dl-card-content"
                ))
            )[:10]  # Limiter aux 10 premiers résultats
            
            print("\nExtraction des informations des médecins...")
            for i, card in enumerate(doctor_cards, 1):
                print(f"\nMédecin {i}:")
                convention_status = self.extract_doctor_info(card)
                print(f"Statut de conventionnement : {convention_status}")
            
            print("\nLe navigateur reste ouvert pour que vous puissiez inspecter les éléments.")
            print("Appuyez sur Ctrl+C dans le terminal pour fermer le navigateur quand vous avez terminé.")
            
            # Garder le navigateur ouvert
            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            print("\nFermeture du navigateur...")
            self.driver.quit()
        except Exception as e:
            print(f"Une erreur est survenue : {str(e)}")
            print("Le navigateur reste ouvert pour inspection.")
            while True:
                time.sleep(1)

def parse_arguments():
    """Parsing des arguments en ligne de commande"""
    parser = argparse.ArgumentParser(description='Scraping Doctolib')
    parser.add_argument('--postal_code', type=str, default="75001", help='Code postal de recherche')
    parser.add_argument('--specialty', type=str, default="Médecin généraliste", help='Spécialité médicale')
    return parser.parse_args()

def main():
    # Charger les variables d'environnement
    load_dotenv()
    
    # Parser les arguments
    args = parse_arguments()
    
    # Créer et lancer le scraper
    scraper = DoctolibScraper()
    scraper.search_doctors(args.postal_code, args.specialty)

if __name__ == "__main__":
    main() 