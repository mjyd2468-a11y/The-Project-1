""" 
    My name is Majyd Muhameed Majyd 
       [.]That for save the information of people in JSON and text file  :)
"""

import json
import re
from pathlib import Path
import cv2
import qrcode
from PIL import Image


DATA_DIR = Path("people")  
INFO_FILE = "info.json"


#========== The helper functions ========== :)
def safe_name(text: str) -> str:
   #====== That to remove invalid characters for file names and replace spaces with underscores ====== :)
    return re.sub(r'[\\/:*?"<>|\s]+', "_", text.strip())


def ask_int(prompt: str) -> int:
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("[!] Please enter a valid integer.")


def ask_float(prompt: str) -> float:
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("[!] Please enter a valid number.")


def ask_phone(prompt: str) -> str:
    while True:
        phone = input(prompt).strip()
        if phone.isdigit() and len(phone) == 11:
            return phone
        print("[!] The phone number must be 11 digits.")

class Information:
    def __init__(self, fname, lname, thname, age, phone,
                 height=None, weight=None, instagram=None, telegram=None):
        self.fname, self.lname, self.thname = fname, lname, thname
        self.age = age
        self.phone = phone
        self.height = height
        self.weight = weight
        self.instagram = instagram
        self.telegram = telegram

#==========The path ========== :)
    @property
    def base(self) -> str:
        return safe_name(f"{self.fname}_{self.lname}_{self.thname}")

    @property
    def folder(self) -> Path:
        return DATA_DIR / self.base

#========== That for JSON and text file ========== :)
    def to_dict(self) -> dict:
        return {
            "fname": self.fname, "lname": self.lname, "thname": self.thname,
            "age": self.age, "phone": self.phone,
            "height": self.height, "weight": self.weight,
            "instagram": self.instagram, "telegram": self.telegram,
        }

    def save(self):
        """يحفظ JSON (للتحميل لاحقاً) + ملف نصي (للقراءة)."""
        self.folder.mkdir(parents=True, exist_ok=True)
        with open(self.folder / INFO_FILE, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        self._write_text_report()

    def _write_text_report(self):
        sections = [
            ("The Name", f"{self.fname} {self.lname} {self.thname}"),
            ("The Age", self.age),
            ("The Phone Number", self.phone),
            ("The Height", self.height),
            ("The Weight", self.weight),
            ("The Instagram", f"https://www.instagram.com/{self.instagram}"
             if self.instagram else None),
            ("The Telegram", f"https://t.me/{self.telegram}"
             if self.telegram else None),
        ]
        with open(self.folder / f"{self.base}.txt", "w", encoding="utf-8") as f:
            for title, value in sections:
                if value not in (None, ""):
                    f.write(f"=========== {title} ===========\n[+] {value}\n\n")

#===That for load and list people=== :)
    @classmethod
    def load(cls, folder: Path) -> "Information":
        with open(folder / INFO_FILE, encoding="utf-8") as f:
            data = json.load(f)
        return cls(**data)

    @staticmethod
    def list_people() -> list[Path]:
        if not DATA_DIR.exists():
            return []
        return sorted(p for p in DATA_DIR.iterdir()
                      if (p / INFO_FILE).is_file())

#==== That foe append Instagram and Telegram ==== :)
    def set_instagram(self, username: str): 
        self.instagram = username.strip().lstrip("@")
        self.save()

    def set_telegram(self, username: str):
        self.telegram = username.strip().lstrip("@")
        self.save()
#that for append height and wedight :)
    def set_height_weight(self, height: float, weight: float):
        self.height, self.weight = height, weight
        self.save()

#==== That for make QR code ==== :)
    def add_qrcode(self):
        data = (f"[+] The name: {self.fname} {self.lname} {self.thname}\n"
                f"[+] The age: {self.age}\n"
                f"[+] The Phone Number: {self.phone}")
        self.folder.mkdir(parents=True, exist_ok=True)
        path = self.folder / f"qr_{self.base}.png"
        qrcode.make(data).save(path)
        print(f"[+] QR saved to {path}")

#==== That to take photo and remove the background ==== :)
    def capture_photo(self):
        """يفتح الكاميرا: SPACE للالتقاط، Q للإلغاء. يرجع مسار الصورة أو None."""
        self.folder.mkdir(parents=True, exist_ok=True)
        photo_path = self.folder / "photo.jpg"

        cam = cv2.VideoCapture(0) 
        if not cam.isOpened():
            print("[!] Could not open camera.")
            return None

        captured = False
        while True:
            ret, frame = cam.read()
            if not ret:
                break

            cv2.imshow("Camera - SPACE to capture, Q to quit", frame)
            key = cv2.waitKey(1) & 0xFF

            if key == 32:  
                cv2.imwrite(str(photo_path), frame)
                print(f"Photo saved as {photo_path}")
                captured = True
                break
            elif key == ord("q"):
                break

        cam.release()
        cv2.destroyAllWindows()

        return photo_path if captured else None

#THE REMOVE BACKGROUND
    def remove_background(self):
        from rembg import remove  

        photo_path = self.capture_photo()
        if photo_path is None:
            print("[!] No photo captured.")
            return

        out = self.folder / "photo_nobg.png"  #_That to change the image path => jpg->png  :)
        remove(Image.open(photo_path)).save(out)
        print(f"[+] Background removed, saved to {out}")

#That to show the person Information :)
    def show(self):
        print("\n--- Current person ---")
        for key, value in self.to_dict().items():
            print(f"{key:10}: {value}")



MENU = """
========================================
1_Add new person
2_Load existing person
3_Add Instagram
4_Add Telegram
5_Add height / weight
6_Add the QR code
7_Remove image background
8_Show current person
9_Exit"""


def choose_person():
    people = Information.list_people()
    if not people:
        print("[!] No saved people yet. Use option 1 first.")
        return None
    print("\nSaved people:")
    for i, p in enumerate(people, 1):
        print(f"  {i}. {p.name}")
    while True:
        raw = input("Enter the number (or 0 to cancel): ").strip()
        if raw == "0":
            return None
        if raw.isdigit() and 1 <= int(raw) <= len(people):
            person = Information.load(people[int(raw) - 1])
            print(f"[+] Loaded: {person.fname} {person.lname} {person.thname}")
            return person
        print("[!] Invalid number.")


def main():
    person = None
    while True:
        print(MENU)
        if person:
            print(f"(current: {person.fname} {person.lname})")
        choice = input("Enter the choice: ").strip()

        if choice == "1":
            person = Information(
                input("Enter the first name: ").strip(),
                input("Enter the last name: ").strip(),
                input("Enter the third name: ").strip(),
                ask_int("Enter the age: "),
                ask_phone("Enter the phone number: "),
                ask_float("Enter the height: "),
                ask_float("Enter the weight: "),
            )
            person.save()
            print(f"[+] Saved in {person.folder}")

        elif choice == "2":
            loaded = choose_person()
            if loaded:
                person = loaded

        elif choice == "9":
            break

        elif choice in {"3", "4", "5", "6", "7", "8"}:
            if person is None:
                print("[!] Add or load a person first (option 1 or 2).")
                continue
            if choice == "3":
                person.set_instagram(input("[+] Instagram username: "))
            elif choice == "4":
                person.set_telegram(input("[+] Telegram username: "))
            elif choice == "5":
                person.set_height_weight(ask_float("Enter the height: "),
                                         ask_float("Enter the weight: "))
            elif choice == "6":
                person.add_qrcode()
            elif choice == "7":
                person.remove_background()
            else:
                person.show()
        else:
            print("[!] Invalid choice, please try again.")

if __name__ == "__main__":
    main()