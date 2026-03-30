"""CEFR level-aware greeting system."""

import logging

logger = logging.getLogger(__name__)


class CEFRGreeter:
    """Generate CEFR-level appropriate greetings.

    Provides level-specific welcome messages to encourage students at their
    appropriate proficiency level.
    """

    # CEFR level greetings (A1-C2)
    GREETINGS = {
        "A1": (
            "🇮🇹 **Ciao!** Welcome to Sofia, your Italian tutor.\n\n"
            "You are at **A1 (Beginner)** level. We will start with simple words and phrases. "
            "Don't worry – every expert was once a beginner! 😊"
        ),
        "A2": (
            "🇮🇹 **Ciao!** Welcome back to Sofia.\n\n"
            "You are at **A2 (Elementary)** level. You already know the basics – let's build "
            "on that foundation with everyday conversations and vocabulary. 📚"
        ),
        "B1": (
            "🇮🇹 **Buongiorno!** Great to see you on Sofia.\n\n"
            "You are at **B1 (Intermediate)** level. You can handle most everyday situations – "
            "time to refine your grammar and expand your vocabulary! 💪"
        ),
        "B2": (
            "🇮🇹 **Buongiorno!** Welcome to your Sofia session.\n\n"
            "You are at **B2 (Upper-Intermediate)** level. You can communicate fluently – "
            "let's push towards near-native precision and idiomatic expression. 🎯"
        ),
        "C1": (
            "🇮🇹 **Buonasera!** Benvenuto su Sofia.\n\n"
            "You are at **C1 (Advanced)** level. Your Italian is very strong – we will focus "
            "on nuance, style, and complex structures. 🏆"
        ),
        "C2": (
            "🇮🇹 **Buonasera!** Benvenuto su Sofia.\n\n"
            "You are at **C2 (Mastery)** level. You have near-native command of Italian – "
            "let's explore literature, culture, and the subtleties of the language. 🌟"
        ),
    }

    GREETING_UNKNOWN = (
        "🇮🇹 **Ciao!** Welcome to Sofia, your personal Italian tutor.\n\n"
        "Your CEFR level has not been determined yet. "
        "Let's start with a quick placement check to tailor the lessons for you! 🎓"
    )

    @classmethod
    def get_greeting(cls, level: str | None) -> str:
        """Get greeting for CEFR level.

        Args:
            level: CEFR level (A1-C2) or None

        Returns:
            Appropriate greeting message
        """
        if not level:
            logger.debug("No CEFR level provided, using default greeting")
            return cls.GREETING_UNKNOWN

        level_upper = level.upper()
        greeting = cls.GREETINGS.get(level_upper, cls.GREETING_UNKNOWN)
        logger.debug("Generated greeting for level: %s", level_upper)
        return greeting

    @classmethod
    def get_available_levels(cls) -> list[str]:
        """Get list of supported CEFR levels.

        Returns:
            List of CEFR level codes (A1, A2, B1, B2, C1, C2)
        """
        return list(cls.GREETINGS.keys())
