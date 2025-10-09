import os
import json
import requests
from typing import Any, Dict, List, Union
import logging
logger = logging.getLogger(__name__)
def ask_question(question: str, table_data: Union[Dict, List, str]) -> str:
    """
    JSON verisi üzerinde OpenRouter API kullanarak soru-cevap ve hesaplama işlemleri yapar.
    
    Args:
        question (str): Sorulacak soru
        table_data (Union[Dict, List, str]): JSON verisi (dict, list veya JSON string)
    
    Returns:
        str: AI'dan gelen cevap
    """
    try:
        # Veriyi JSON formatına dönüştür
        if isinstance(table_data, str):
            try:
                data = json.loads(table_data)
            except json.JSONDecodeError:
                return "Hata: Geçersiz JSON formatı"
        else:
            data = table_data
        
        # Veriyi string formatına çevir (AI'ya göndermek için)
        data_str = json.dumps(data, ensure_ascii=False, indent=2)
        
        # OpenRouter API anahtarını kontrol et
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            return "Hata: OPENROUTER_API_KEY environment variable bulunamadı"
        
        # Prompt hazırla
        system_prompt = """Sen bir veri analisti ve hesaplama uzmanısın. JSON verisi üzerinde analiz yapabilir, hesaplamalar gerçekleştirebilir ve soruları yanıtlayabilirsin. 
Görevlerin:
1. Verilen JSON verisini analiz et
2. Kullanıcının sorusunu anla
3. Gerekli hesaplamaları yap
4. Sonuçları açık ve anlaşılır şekilde sun

Sadece verilen veri üzerinde çalış ve gerçek hesaplamalar yap. Matematiksel işlemler için Python tarzı hesaplama göster."""

        user_prompt = f"""
Aşağıdaki JSON verisi var:

{data_str}

Soru: {question}

Bu soruyu yanıtlamak için veriyi analiz et, gerekli hesaplamaları yap ve sonucu açıkla.
"""

                
        # OpenRouter API'ye istek gönder
        headers = {
            "Authorization": f"Bearer {"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"}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "meta-llama/llama-3.1-8b-instruct:free",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 1000
        }
        
        logger.info("API isteği gönderiliyor...")
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30  # Timeout süresini düşürdüm
        )
        
        logger.info(f"API yanıt kodu: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                answer = result['choices'][0]['message']['content']
                logger.info("Başarılı yanıt alındı")
                return answer
            except (KeyError, IndexError) as e:
                logger.error(f"API yanıt parse hatası: {e}")
                return f"Hata: API yanıtı beklenmeyen formatta - {str(e)}"
        else:
            error_msg = f"API Hatası: {response.status_code}"
            try:
                error_detail = response.json()
                if 'error' in error_detail:
                    error_msg += f" - {error_detail['error'].get('message', 'Bilinmeyen hata')}"
            except:
                error_msg += f" - {response.text[:200]}"
            
            logger.error(error_msg)
            return error_msg
            
    except requests.exceptions.Timeout:
        logger.error("Timeout hatası")
        return "Hata: API isteği zaman aşımına uğradı"
    except requests.exceptions.ConnectionError:
        logger.error("Bağlantı hatası")
        return "Hata: İnternet bağlantısı problemi"
    except requests.exceptions.RequestException as e:
        logger.error(f"Request hatası: {e}")
        return f"Hata: API isteği başarısız - {str(e)}"
    except json.JSONDecodeError as e:
        logger.error(f"JSON hatası: {e}")
        return f"Hata: JSON işleme hatası - {str(e)}"
    except Exception as e:
        logger.error(f"Beklenmeyen hata: {e}", exc_info=True)
        return f"Hata: Beklenmeyen bir sorun oluştu - {str(e)}"




"""import os
import pandas as pd
from pandasai import Agent

def ask_question(question, table_data):
    try:
        if not isinstance(table_data, list):
            table_data = [table_data]
            
        df = pd.DataFrame(table_data)
        df.columns = ['_'.join(filter(None, map(str, col))) for col in df.columns]
        for col in df.columns:
            if df[col].dtype == 'object':  
                try:
                    df[col] = df[col].str.replace(',', '.').astype(float)
                except ValueError:
                    pass
    

        
        os.environ["PANDASAI_API_KEY"] = os.getenv('pandas_api')
        agent = Agent(df)
        
        
        response = agent.chat(str(question))  
        print(df)
        return str(response)
    except Exception as e:
        return f"Error processing question: {str(e)}"
"""