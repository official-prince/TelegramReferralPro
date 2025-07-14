"""Multilingual support for the referral bot"""

import logging
from typing import Dict, Optional, Any
from enum import Enum

logger = logging.getLogger(__name__)

class SupportedLanguage(Enum):
    """Supported languages for the bot"""
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    RUSSIAN = "ru"
    ARABIC = "ar"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"
    HINDI = "hi"
    TURKISH = "tr"
    DUTCH = "nl"
    POLISH = "pl"

class LanguageDetector:
    """Detect user language based on various signals"""
    
    @staticmethod
    def detect_from_telegram_user(user) -> str:
        """Detect language from Telegram user data"""
        if hasattr(user, 'language_code') and user.language_code:
            # Map common Telegram language codes to our supported languages
            lang_map = {
                'en': SupportedLanguage.ENGLISH.value,
                'es': SupportedLanguage.SPANISH.value,
                'fr': SupportedLanguage.FRENCH.value,
                'de': SupportedLanguage.GERMAN.value,
                'it': SupportedLanguage.ITALIAN.value,
                'pt': SupportedLanguage.PORTUGUESE.value,
                'ru': SupportedLanguage.RUSSIAN.value,
                'ar': SupportedLanguage.ARABIC.value,
                'zh': SupportedLanguage.CHINESE.value,
                'ja': SupportedLanguage.JAPANESE.value,
                'ko': SupportedLanguage.KOREAN.value,
                'hi': SupportedLanguage.HINDI.value,
                'tr': SupportedLanguage.TURKISH.value,
                'nl': SupportedLanguage.DUTCH.value,
                'pl': SupportedLanguage.POLISH.value,
            }
            
            # Handle language codes with region (e.g., 'en-US' -> 'en')
            base_lang = user.language_code.split('-')[0].lower()
            return lang_map.get(base_lang, SupportedLanguage.ENGLISH.value)
        
        return SupportedLanguage.ENGLISH.value

    @staticmethod
    def detect_from_text(text: str) -> str:
        """Basic text-based language detection using common words"""
        if not text:
            return SupportedLanguage.ENGLISH.value
        
        text_lower = text.lower()
        
        # Language detection patterns (common words/phrases)
        patterns = {
            SupportedLanguage.SPANISH.value: ['hola', 'gracias', 'por favor', 'si', 'no', 'buenos dias', 'buenas tardes'],
            SupportedLanguage.FRENCH.value: ['bonjour', 'merci', 'oui', 'non', 'salut', 'bonsoir', 'au revoir'],
            SupportedLanguage.GERMAN.value: ['hallo', 'danke', 'bitte', 'ja', 'nein', 'guten tag', 'auf wiedersehen'],
            SupportedLanguage.ITALIAN.value: ['ciao', 'grazie', 'prego', 'si', 'no', 'buongiorno', 'buonasera'],
            SupportedLanguage.PORTUGUESE.value: ['ola', 'obrigado', 'por favor', 'sim', 'nao', 'bom dia', 'boa tarde'],
            SupportedLanguage.RUSSIAN.value: ['привет', 'спасибо', 'пожалуйста', 'да', 'нет', 'здравствуйте'],
            SupportedLanguage.ARABIC.value: ['مرحبا', 'شكرا', 'من فضلك', 'نعم', 'لا', 'السلام عليكم'],
            SupportedLanguage.CHINESE.value: ['你好', '谢谢', '请', '是', '不是', '早上好'],
            SupportedLanguage.JAPANESE.value: ['こんにちは', 'ありがとう', 'はい', 'いいえ', 'おはよう'],
            SupportedLanguage.KOREAN.value: ['안녕하세요', '감사합니다', '네', '아니요', '좋은 아침'],
            SupportedLanguage.HINDI.value: ['नमस्ते', 'धन्यवाद', 'कृपया', 'हाँ', 'नहीं'],
            SupportedLanguage.TURKISH.value: ['merhaba', 'teşekkür', 'lütfen', 'evet', 'hayır', 'günaydın'],
            SupportedLanguage.DUTCH.value: ['hallo', 'dank je', 'alstublieft', 'ja', 'nee', 'goedemorgen'],
            SupportedLanguage.POLISH.value: ['cześć', 'dziękuję', 'proszę', 'tak', 'nie', 'dzień dobry'],
        }
        
        # Count matches for each language
        scores = {}
        for lang, words in patterns.items():
            score = sum(1 for word in words if word in text_lower)
            if score > 0:
                scores[lang] = score
        
        # Return language with highest score, default to English
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        
        return SupportedLanguage.ENGLISH.value

class MultilingualMessages:
    """Message translations for different languages"""
    
    MESSAGES = {
        SupportedLanguage.ENGLISH.value: {
            "welcome_new_user": """
🎉 Welcome to the referral system!

To get started:
1. First, join our channel: {channel_link}
2. Once you join, I'll give you your unique referral link
3. Share your link with friends to earn rewards!

Click the link above to join the channel, then come back here.
""",
            "welcome_existing_member": """
🎉 Welcome back! I can see you're already a member of {channel_name}.

Here's your unique referral link:
{referral_link}

📋 **Your Mission:**
Share this link with friends and get {target} people to join the channel using your link to earn your reward!

🔗 **How it works:**
1. Share your referral link with friends
2. When they click it and join the channel, you get credit
3. Reach {target} successful referrals to claim your reward

Use /status to check your progress anytime!
""",
            "channel_joined_success": """
✅ Great! You've successfully joined {channel_name}!

Here's your unique referral link:
{referral_link}

📋 **Your Mission:**
Share this link with friends and get {target} people to join the channel using your link to earn your reward!

🔗 **How it works:**
1. Share your referral link with friends
2. When they click it and join the channel, you get credit
3. Reach {target} successful referrals to claim your reward

Use /status to check your progress anytime!
""",
            "referral_welcome": """
👋 Welcome! You were referred by a friend.

Please join our channel to continue: {channel_link}

After joining, you'll get your own referral link to start earning rewards too!
""",
            "status_message": """
📊 **Your Referral Status**

👥 Active Referrals: {active_referrals}/{target}
📈 Total Referrals Made: {total_referrals}
🎯 Target: {target} referrals
🔥 Remaining: {remaining}
📊 Progress: {progress}%

{progress_bar}

{status_text}
""",
            "reward_available": """
🎉 **CONGRATULATIONS!** 🎉

You've reached your referral target! Your reward is ready to claim.

Use /claim to get your reward!
""",
            "reward_claimed": """
🏆 **REWARD CLAIMED!** 🏆

{reward_message}

Thank you for helping grow our community! Keep sharing your referral link to help even more people discover our channel.

Your referral link is still active: {referral_link}
""",
            "help_message": """
🤖 **Referral Bot Commands**

/start - Get your referral link and instructions
/status - Check your referral progress
/claim - Claim your reward (when target is reached)
/help - Show this help message
/language - Change language settings

📋 **How the referral system works:**
1. Get your unique referral link from /start
2. Share it with friends
3. When friends join using your link, you get credit
4. Reach the target number of referrals to earn rewards
5. Use /claim to get your reward

💡 **Tips:**
- Share your link in groups, social media, or with friends
- Only active channel members count towards your target
- If someone leaves the channel, they won't count anymore
- You can check your progress anytime with /status
""",
            "error_not_channel_member": """
❌ You need to be a member of the channel first!

Join here: {channel_link}

After joining, come back and use /start again.
""",
            "error_reward_already_claimed": """
✅ You've already claimed your reward!

Your referral link is still active if you want to keep helping grow the community: {referral_link}
""",
            "error_reward_not_available": """
❌ You haven't reached the referral target yet.

Current progress: {active_referrals}/{target}

Use /status to see your detailed progress.
""",
            "language_selection": """
🌍 **Select Your Language / Selecciona tu idioma / Choisissez votre langue**

Choose your preferred language:
""",
            "language_changed": """
✅ Language changed to English!

All future messages will be in English.
""",
            "progress_bar_full": "🟩",
            "progress_bar_empty": "⬜",
            "status_target_reached": "🎉 Target reached! Use /claim to get your reward!",
            "status_no_referrals": "🚀 Start sharing your referral link to earn rewards!",
            "status_progress": "🔥 Great progress! Just {remaining} more referrals to go!",
        },
        
        SupportedLanguage.SPANISH.value: {
            "welcome_new_user": """
🎉 ¡Bienvenido al sistema de referidos!

Para comenzar:
1. Primero, únete a nuestro canal: {channel_link}
2. Una vez que te unas, te daré tu enlace de referido único
3. ¡Comparte tu enlace con amigos para ganar recompensas!

Haz clic en el enlace de arriba para unirte al canal, luego regresa aquí.
""",
            "welcome_existing_member": """
🎉 ¡Bienvenido de vuelta! Veo que ya eres miembro de {channel_name}.

Aquí está tu enlace de referido único:
{referral_link}

📋 **Tu Misión:**
¡Comparte este enlace con amigos y consigue que {target} personas se unan al canal usando tu enlace para ganar tu recompensa!

🔗 **Cómo funciona:**
1. Comparte tu enlace de referido con amigos
2. Cuando hagan clic y se unan al canal, obtienes crédito
3. Alcanza {target} referidos exitosos para reclamar tu recompensa

¡Usa /status para verificar tu progreso en cualquier momento!
""",
            "channel_joined_success": """
✅ ¡Genial! ¡Te has unido exitosamente a {channel_name}!

Aquí está tu enlace de referido único:
{referral_link}

📋 **Tu Misión:**
¡Comparte este enlace con amigos y consigue que {target} personas se unan al canal usando tu enlace para ganar tu recompensa!

🔗 **Cómo funciona:**
1. Comparte tu enlace de referido con amigos
2. Cuando hagan clic y se unan al canal, obtienes crédito
3. Alcanza {target} referidos exitosos para reclamar tu recompensa

¡Usa /status para verificar tu progreso en cualquier momento!
""",
            "referral_welcome": """
👋 ¡Bienvenido! Fuiste referido por un amigo.

Por favor únete a nuestro canal para continuar: {channel_link}

¡Después de unirte, obtendrás tu propio enlace de referido para comenzar a ganar recompensas también!
""",
            "status_message": """
📊 **Estado de tus Referidos**

👥 Referidos Activos: {active_referrals}/{target}
📈 Total de Referidos Hechos: {total_referrals}
🎯 Objetivo: {target} referidos
🔥 Restantes: {remaining}
📊 Progreso: {progress}%

{progress_bar}

{status_text}
""",
            "reward_available": """
🎉 **¡FELICITACIONES!** 🎉

¡Has alcanzado tu objetivo de referidos! Tu recompensa está lista para reclamar.

¡Usa /claim para obtener tu recompensa!
""",
            "reward_claimed": """
🏆 **¡RECOMPENSA RECLAMADA!** 🏆

{reward_message}

¡Gracias por ayudar a hacer crecer nuestra comunidad! Sigue compartiendo tu enlace de referido para ayudar a que aún más personas descubran nuestro canal.

Tu enlace de referido sigue activo: {referral_link}
""",
            "help_message": """
🤖 **Comandos del Bot de Referidos**

/start - Obtén tu enlace de referido e instrucciones
/status - Verifica tu progreso de referidos
/claim - Reclama tu recompensa (cuando se alcance el objetivo)
/help - Muestra este mensaje de ayuda
/language - Cambiar configuración de idioma

📋 **Cómo funciona el sistema de referidos:**
1. Obtén tu enlace único de referido desde /start
2. Compártelo con amigos
3. Cuando los amigos se unan usando tu enlace, obtienes crédito
4. Alcanza el número objetivo de referidos para ganar recompensas
5. Usa /claim para obtener tu recompensa

💡 **Consejos:**
- Comparte tu enlace en grupos, redes sociales, o con amigos
- Solo los miembros activos del canal cuentan para tu objetivo
- Si alguien deja el canal, ya no contará
- Puedes verificar tu progreso en cualquier momento con /status
""",
            "error_not_channel_member": """
❌ ¡Necesitas ser miembro del canal primero!

Únete aquí: {channel_link}

Después de unirte, regresa y usa /start otra vez.
""",
            "error_reward_already_claimed": """
✅ ¡Ya has reclamado tu recompensa!

Tu enlace de referido sigue activo si quieres seguir ayudando a hacer crecer la comunidad: {referral_link}
""",
            "error_reward_not_available": """
❌ Aún no has alcanzado el objetivo de referidos.

Progreso actual: {active_referrals}/{target}

Usa /status para ver tu progreso detallado.
""",
            "language_selection": """
🌍 **Selecciona tu Idioma / Select Your Language / Choisissez votre langue**

Elige tu idioma preferido:
""",
            "language_changed": """
✅ ¡Idioma cambiado a Español!

Todos los mensajes futuros serán en español.
""",
            "progress_bar_full": "🟩",
            "progress_bar_empty": "⬜",
            "status_target_reached": "🎉 ¡Objetivo alcanzado! ¡Usa /claim para obtener tu recompensa!",
            "status_no_referrals": "🚀 ¡Comienza a compartir tu enlace de referido para ganar recompensas!",
            "status_progress": "🔥 ¡Gran progreso! ¡Solo {remaining} referidos más para llegar!",
        },
        
        SupportedLanguage.FRENCH.value: {
            "welcome_new_user": """
🎉 Bienvenue dans le système de parrainage !

Pour commencer :
1. D'abord, rejoignez notre chaîne : {channel_link}
2. Une fois que vous rejoignez, je vous donnerai votre lien de parrainage unique
3. Partagez votre lien avec des amis pour gagner des récompenses !

Cliquez sur le lien ci-dessus pour rejoindre la chaîne, puis revenez ici.
""",
            "welcome_existing_member": """
🎉 Bon retour ! Je vois que vous êtes déjà membre de {channel_name}.

Voici votre lien de parrainage unique :
{referral_link}

📋 **Votre Mission :**
Partagez ce lien avec des amis et obtenez {target} personnes pour rejoindre la chaîne en utilisant votre lien pour gagner votre récompense !

🔗 **Comment ça marche :**
1. Partagez votre lien de parrainage avec des amis
2. Quand ils cliquent et rejoignent la chaîne, vous obtenez du crédit
3. Atteignez {target} parrainages réussis pour réclamer votre récompense

Utilisez /status pour vérifier votre progression à tout moment !
""",
            "channel_joined_success": """
✅ Génial ! Vous avez rejoint avec succès {channel_name} !

Voici votre lien de parrainage unique :
{referral_link}

📋 **Votre Mission :**
Partagez ce lien avec des amis et obtenez {target} personnes pour rejoindre la chaîne en utilisant votre lien pour gagner votre récompense !

🔗 **Comment ça marche :**
1. Partagez votre lien de parrainage avec des amis
2. Quand ils cliquent et rejoignent la chaîne, vous obtenez du crédit
3. Atteignez {target} parrainages réussis pour réclamer votre récompense

Utilisez /status pour vérifier votre progression à tout moment !
""",
            "referral_welcome": """
👋 Bienvenue ! Vous avez été parrainé par un ami.

Veuillez rejoindre notre chaîne pour continuer : {channel_link}

Après avoir rejoint, vous obtiendrez votre propre lien de parrainage pour commencer à gagner des récompenses aussi !
""",
            "status_message": """
📊 **Statut de votre Parrainage**

👥 Parrainages Actifs : {active_referrals}/{target}
📈 Total des Parrainages Faits : {total_referrals}
🎯 Objectif : {target} parrainages
🔥 Restants : {remaining}
📊 Progression : {progress}%

{progress_bar}

{status_text}
""",
            "reward_available": """
🎉 **FÉLICITATIONS !** 🎉

Vous avez atteint votre objectif de parrainage ! Votre récompense est prête à être réclamée.

Utilisez /claim pour obtenir votre récompense !
""",
            "reward_claimed": """
🏆 **RÉCOMPENSE RÉCLAMÉE !** 🏆

{reward_message}

Merci d'avoir aidé à faire grandir notre communauté ! Continuez à partager votre lien de parrainage pour aider encore plus de personnes à découvrir notre chaîne.

Votre lien de parrainage est toujours actif : {referral_link}
""",
            "help_message": """
🤖 **Commandes du Bot de Parrainage**

/start - Obtenez votre lien de parrainage et les instructions
/status - Vérifiez votre progression de parrainage
/claim - Réclamez votre récompense (quand l'objectif est atteint)
/help - Affichez ce message d'aide
/language - Changer les paramètres de langue

📋 **Comment fonctionne le système de parrainage :**
1. Obtenez votre lien unique de parrainage depuis /start
2. Partagez-le avec des amis
3. Quand les amis rejoignent en utilisant votre lien, vous obtenez du crédit
4. Atteignez le nombre cible de parrainages pour gagner des récompenses
5. Utilisez /claim pour obtenir votre récompense

💡 **Conseils :**
- Partagez votre lien dans des groupes, sur les réseaux sociaux, ou avec des amis
- Seuls les membres actifs de la chaîne comptent pour votre objectif
- Si quelqu'un quitte la chaîne, il ne comptera plus
- Vous pouvez vérifier votre progression à tout moment avec /status
""",
            "error_not_channel_member": """
❌ Vous devez d'abord être membre de la chaîne !

Rejoignez ici : {channel_link}

Après avoir rejoint, revenez et utilisez /start à nouveau.
""",
            "error_reward_already_claimed": """
✅ Vous avez déjà réclamé votre récompense !

Votre lien de parrainage est toujours actif si vous voulez continuer à aider la communauté à grandir : {referral_link}
""",
            "error_reward_not_available": """
❌ Vous n'avez pas encore atteint l'objectif de parrainage.

Progression actuelle : {active_referrals}/{target}

Utilisez /status pour voir votre progression détaillée.
""",
            "language_selection": """
🌍 **Sélectionnez votre Langue / Select Your Language / Selecciona tu idioma**

Choisissez votre langue préférée :
""",
            "language_changed": """
✅ Langue changée en Français !

Tous les futurs messages seront en français.
""",
            "progress_bar_full": "🟩",
            "progress_bar_empty": "⬜",
            "status_target_reached": "🎉 Objectif atteint ! Utilisez /claim pour obtenir votre récompense !",
            "status_no_referrals": "🚀 Commencez à partager votre lien de parrainage pour gagner des récompenses !",
            "status_progress": "🔥 Excellente progression ! Plus que {remaining} parrainages à faire !",
        }
    }
    
    @staticmethod
    def get_message(lang: str, key: str, fallback: str = None, **kwargs) -> str:
        """Get a message in the specified language"""
        # Fallback to English if language not supported
        if lang not in MultilingualMessages.MESSAGES:
            lang = SupportedLanguage.ENGLISH.value
        
        # Fallback to English message if key not found
        if key not in MultilingualMessages.MESSAGES[lang]:
            if key in MultilingualMessages.MESSAGES[SupportedLanguage.ENGLISH.value]:
                message = MultilingualMessages.MESSAGES[SupportedLanguage.ENGLISH.value][key]
            elif fallback:
                message = fallback
            else:
                return f"Message key '{key}' not found"
        else:
            message = MultilingualMessages.MESSAGES[lang][key]
        
        # Format the message with provided arguments
        try:
            return message.format(**kwargs)
        except KeyError as e:
            logger.warning(f"Missing format key {e} for message {key} in language {lang}")
            return message
    
    @staticmethod
    def get_available_languages() -> Dict[str, str]:
        """Get list of available languages with their names"""
        return {
            SupportedLanguage.ENGLISH.value: "🇺🇸 English",
            SupportedLanguage.SPANISH.value: "🇪🇸 Español", 
            SupportedLanguage.FRENCH.value: "🇫🇷 Français",
            SupportedLanguage.GERMAN.value: "🇩🇪 Deutsch",
            SupportedLanguage.ITALIAN.value: "🇮🇹 Italiano",
            SupportedLanguage.PORTUGUESE.value: "🇵🇹 Português",
            SupportedLanguage.RUSSIAN.value: "🇷🇺 Русский",
            SupportedLanguage.ARABIC.value: "🇸🇦 العربية",
            SupportedLanguage.CHINESE.value: "🇨🇳 中文",
            SupportedLanguage.JAPANESE.value: "🇯🇵 日本語",
            SupportedLanguage.KOREAN.value: "🇰🇷 한국어",
            SupportedLanguage.HINDI.value: "🇮🇳 हिन्दी",
            SupportedLanguage.TURKISH.value: "🇹🇷 Türkçe",
            SupportedLanguage.DUTCH.value: "🇳🇱 Nederlands",
            SupportedLanguage.POLISH.value: "🇵🇱 Polski",
        }

class LanguageManager:
    """Manage user language preferences"""
    
    def __init__(self, database):
        self.db = database
        self._init_language_table()
    
    def _init_language_table(self):
        """Initialize language preferences table"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_languages (
                        user_id INTEGER PRIMARY KEY,
                        language_code TEXT DEFAULT 'en',
                        detected_language TEXT,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                conn.commit()
                logger.info("Language table initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing language table: {e}")
    
    def set_user_language(self, user_id: int, language_code: str, detected: bool = False) -> bool:
        """Set user's preferred language"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                if detected:
                    cursor.execute('''
                        INSERT OR REPLACE INTO user_languages 
                        (user_id, language_code, detected_language, updated_at)
                        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                    ''', (user_id, language_code, language_code))
                else:
                    cursor.execute('''
                        INSERT OR REPLACE INTO user_languages 
                        (user_id, language_code, updated_at)
                        VALUES (?, ?, CURRENT_TIMESTAMP)
                    ''', (user_id, language_code))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error setting user language: {e}")
            return False
    
    def get_user_language(self, user_id: int) -> str:
        """Get user's preferred language"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT language_code FROM user_languages WHERE user_id = ?', (user_id,))
                result = cursor.fetchone()
                if result:
                    return result[0]
        except Exception as e:
            logger.error(f"Error getting user language: {e}")
        
        return SupportedLanguage.ENGLISH.value
    
    def detect_and_set_language(self, user_id: int, telegram_user, message_text: str = None) -> str:
        """Detect and set user language based on available signals"""
        # First try to get existing preference
        existing_lang = self.get_user_language(user_id)
        if existing_lang != SupportedLanguage.ENGLISH.value:
            return existing_lang
        
        # Detect from Telegram user data
        detected_lang = LanguageDetector.detect_from_telegram_user(telegram_user)
        
        # If we have message text, also try text detection
        if message_text and message_text.strip():
            text_lang = LanguageDetector.detect_from_text(message_text)
            # Prefer text detection if it's not English (more specific)
            if text_lang != SupportedLanguage.ENGLISH.value:
                detected_lang = text_lang
        
        # Set the detected language
        self.set_user_language(user_id, detected_lang, detected=True)
        return detected_lang