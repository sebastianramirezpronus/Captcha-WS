from selenium import webdriver
import time
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import requests
import whisper
import warnings
from selenium.webdriver.chrome.options import Options

warnings.filterwarnings("ignore")
model = whisper.load_model("base") # Hay varios tipos de modelo, el "base" representa que es el modelo normal
    
def click_checkbox(driver):
    driver.switch_to.default_content()
    driver.switch_to.frame(driver.find_element(By.XPATH, ".//iframe[@title='reCAPTCHA']")) # iframe es el cuadro en el que guardan el CAPTCHA para no sea clickeable
    driver.find_element(By.ID, "recaptcha-anchor-label").click() 
    driver.switch_to.default_content() # Los comandos "switch_to.default_content()" cambian entre los iframes y la ventana normal

def request_audio_version(driver):
    driver.switch_to.default_content() 
    driver.switch_to.frame(driver.find_element(By.XPATH, "/html/body/div[2]/div[4]/iframe"))
    driver.find_element(By.ID, "recaptcha-audio-button").click() # Busco el acceso al CAPTCHA de audio

def solve_audio_captcha(driver):
    # audio=driver.find_element(By.XPATH,'/html/body/div/div/div[3]/div/button').click()
    text = transcribe(driver.find_element(By.XPATH, "/html/body/div/div/div[3]/audio").get_attribute('src')) ## Acá envío el audio al modelo, el audio va vía e link de "src"
    for letras in text:
        driver.find_element(By.XPATH, "/html/body/div/div/div[6]/input").send_keys(letras) # Envío letra por letra para que no se borre una letra con otra.
    driver.find_element(By.ID, "recaptcha-verify-button").click()
    driver.switch_to.default_content()
    driver.find_element(By.XPATH,'/html/body/div[1]/form/fieldset/ul/li[6]/input').click()

def transcribe(url):
    filename = 'audio.wav' # Creo un archivo vacío de audio.
    with open(filename, 'wb') as f:
        f.write(requests.get(url).content) # Convierto la url a wav escribiendo en binario sobre el archivo

    model = whisper.load_model("base")

    audio = whisper.load_audio("audio.wav") # Cargo el audio a la base.
    audio = whisper.pad_or_trim(audio) 
    mel = whisper.log_mel_spectrogram(audio).to(model.device) # Conversión al modo de lectura del modelo.

    # Detecetar el idioma que habla, es más una curiosidad para la prueba, se puede omitir.

    _, probs = model.detect_language(mel)
    print(f"Detected language: {max(probs, key=probs.get)}") 

    # Decodificar el audio.

    options = whisper.DecodingOptions(fp16 = False) 
    result = whisper.decode(model, mel, options) 
    return result.text # Obtengo la transcripción del texto del audio y continua el proceso de "solve_audio_captcha_driver"


if __name__ == "__main__":
    driver = webdriver.Chrome(executable_path=ChromeDriverManager().install())
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True) # Evita que cierre la ventana a pesar del error.
    chrome_options.add_argument("--lang=en-US") # Correr el navegador en inglés para evitar el cambio de nombre de ciertos elementos.
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.get("https://www.google.com/recaptcha/api2/demo")
    click_checkbox(driver)
    time.sleep(1)
    request_audio_version(driver)
    time.sleep(1)
    solve_audio_captcha(driver)
    time.sleep(10)