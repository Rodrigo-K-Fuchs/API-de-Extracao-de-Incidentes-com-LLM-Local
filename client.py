import sys
from datetime import datetime

from core.incident_extractor import IncidentExtractor


def main():
    # Data de referência para resolver "amanha", "ontem", etc.
    reference_date = datetime.now()

    extractor = IncidentExtractor(
        model="llama3.2",
        reference_date=reference_date,
        temperature=0.0,
    )

    # Texto vindo por argumento ou stdin
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        print("Digite um texto para teste (ENTER finaliza):\n")
        text = input("> ")

    if not text.strip():
        print("Texto vazio. Nem a LLM merece esse desprezo.")
        return

    print("\n" + "=" * 80)
    print("TEXTO ORIGINAL")
    print("=" * 80)
    print(text)

    try:
        result = extractor.extract_dict(text)

        print("\n" + "=" * 80)
        print("JSON EXTRAÍDO PELA LLM")
        print("=" * 80)
        print(result)

    except Exception as e:
        print("\n" + "=" * 80)
        print("ERRO NA EXTRAÇÃO")
        print("=" * 80)
        print(str(e))

    print("\n" + "=" * 80)
    print("FIM DO TESTE")
    print("=" * 80)


if __name__ == "__main__":
    main()