import enum


class TypeMission(str, enum.Enum):
    NATIONALE="Nationale"
    INTERNATIONALE="Internationale"

class EtatMission(str, enum.Enum):
    OUVERTE="Ouverte"
    EN_ATTENTE="En attente"
    VALIDEE="Validee"
    REFUSEE="Refusee"

class TypeFinancementEnum(str, enum.Enum):
    PERSONNEL = "PERSONNEL"
    PARRAINAGE = "PARRAINAGE"
    INTERNE = "INTERNE"