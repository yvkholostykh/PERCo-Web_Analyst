#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PERCo-Web Аналитик v4.3 - Исправление ошибок копирования
"""

import sys
import os
import subprocess
import importlib.util
import time
import threading
import re
import shutil
import tempfile
import json
import base64
import traceback
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, font

# ===================== ИНФОРМАЦИЯ ОБ АВТОРЕ =====================
AUTHOR = "Специалист по информационной безопасности, Ю. В. Холостых"
GITHUB = "https://github.com/yvkholostykh?tab=repositories"
LICENSE = "MINT"
PROGRAM_NAME = "PERCo-Web Аналитик"
VERSION = "4.3"
# ================================================================

# ---------- УЛУЧШЕННАЯ СИСТЕМА УСТАНОВКИ БИБЛИОТЕК ----------
class LibraryInstaller:
    """Класс для установки и управления библиотеками"""
    
    def __init__(self):
        self.target_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib")
        self.site_packages = os.path.join(self.target_dir, 'site-packages')
        self.required_libs = {
            'pandas': 'pandas',
            'openpyxl': 'openpyxl',
            'requests': 'requests',
            'urllib3': 'urllib3',
            'Pillow': 'PIL'
        }
        self.installed_libs = []
        self.errors = []
        
    def setup(self):
        """Основной метод установки"""
        print("\n" + "="*70)
        print("*** УСТАНОВКА НЕОБХОДИМЫХ БИБЛИОТЕК ***")
        print("="*70)
        
        os.makedirs(self.target_dir, exist_ok=True)
        os.makedirs(self.site_packages, exist_ok=True)
        
        if self.target_dir not in sys.path:
            sys.path.insert(0, self.target_dir)
        if self.site_packages not in sys.path:
            sys.path.insert(0, self.site_packages)
        
        missing = self.check_libraries()
        
        if missing:
            print(f"\n⚠️ Не найдены библиотеки: {', '.join(missing)}")
            print(f"📦 Начинаю установку в: {self.target_dir}")
            
            for lib_name in missing:
                if not self.install_library(lib_name):
                    self.errors.append(f"Не удалось установить {lib_name}")
            
            if self.errors:
                print("\n❌ Ошибки при установке:")
                for err in self.errors:
                    print(f"  • {err}")
                return False
            
            importlib.invalidate_caches()
            final_check = self.check_libraries()
            if final_check:
                print(f"\n⚠️ После установки не загружены: {final_check}")
                print("Пожалуйста, перезапустите программу")
                return False
            
            print("\n✅ Все библиотеки успешно установлены!")
        else:
            print("\n✅ Все необходимые библиотеки уже установлены.")
        
        print("="*70 + "\n")
        return True
    
    def check_libraries(self):
        """Проверка наличия библиотек"""
        missing = []
        for display_name, import_name in self.required_libs.items():
            print(f"  >> Проверка '{display_name}'...", end=' ')
            try:
                if importlib.util.find_spec(import_name) is not None:
                    print("[OK]")
                else:
                    print("[НЕ НАЙДЕНА]")
                    missing.append(display_name)
            except Exception as e:
                print(f"[ОШИБКА]")
                missing.append(display_name)
        return missing
    
    def install_library(self, lib_name):
        """Установка одной библиотеки с несколькими попытками"""
        print(f"  >> Установка {lib_name}...", end=' ')
        
        if lib_name == 'Pillow':
            return self.install_pillow()
        
        return self.install_with_pip(lib_name)
    
    def install_pillow(self):
        """Специальная установка Pillow с несколькими попытками"""
        print(f"\n  >> Специальная установка Pillow...")
        
        if self.install_with_pip('Pillow'):
            return True
        
        print(f"  >> Попытка 2: установка Pillow с версией...", end=' ')
        if self.install_with_pip('Pillow==10.1.0'):
            return True
        
        print(f"  >> Попытка 3: установка Pillow без кэша...", end=' ')
        try:
            cmd = [
                sys.executable, "-m", "pip", "install", "Pillow",
                "--target", self.target_dir,
                "--no-cache-dir",
                "--upgrade"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            if result.returncode == 0:
                print("[ГОТОВО]")
                return True
            else:
                print("[ОШИБКА]")
                return False
        except Exception as e:
            print(f"[ОШИБКА]")
            return False
    
    def install_with_pip(self, package):
        """Установка через pip"""
        try:
            cmd = [
                sys.executable, "-m", "pip", "install", package,
                "--target", self.target_dir,
                "--upgrade",
                "--no-cache-dir",
                "--disable-pip-version-check"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            if result.returncode == 0:
                return True
            else:
                return False
        except:
            return False

# ---------- УСТАНОВКА БИБЛИОТЕК ----------
installer = LibraryInstaller()
if not installer.setup():
    error_root = tk.Tk()
    error_root.title("Ошибка установки")
    error_root.geometry("650x500")
    error_root.resizable(True, True)
    error_root.configure(bg='#f5f5f7')
    
    title_label = tk.Label(error_root, text="❌ ОШИБКА УСТАНОВКИ БИБЛИОТЕК", 
                          font=("Segoe UI", 14, "bold"), bg='#f5f5f7', fg='#e74c3c')
    title_label.pack(pady=(20, 10))
    
    error_text = scrolledtext.ScrolledText(error_root, wrap=tk.WORD, 
                                           font=("Consolas", 10), bg='#ffffff',
                                           fg='#1a1a2e', relief="flat", bd=1,
                                           padx=10, pady=10)
    error_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    error_text.insert(tk.END, "Не удалось установить следующие библиотеки:\n\n")
    for err in installer.errors:
        error_text.insert(tk.END, f"  • {err}\n")
    
    error_text.insert(tk.END, "\n" + "="*60 + "\n")
    error_text.insert(tk.END, "🔧 РЕШЕНИЕ:\n\n")
    error_text.insert(tk.END, "1. Запустите программу от имени администратора\n")
    error_text.insert(tk.END, "2. Установите библиотеки вручную:\n")
    for lib in installer.required_libs.keys():
        error_text.insert(tk.END, f"   pip install {lib}\n")
    
    error_text.insert(tk.END, "\n3. Для Pillow попробуйте отдельно:\n")
    error_text.insert(tk.END, "   pip install Pillow --upgrade\n")
    
    error_text.config(state=tk.DISABLED)
    
    btn_frame = tk.Frame(error_root, bg='#f5f5f7')
    btn_frame.pack(pady=10)
    
    close_btn = tk.Button(btn_frame, text="Закрыть", command=error_root.destroy,
                         font=("Segoe UI", 11), bg="#e74c3c", fg="white",
                         padx=30, pady=8, relief="flat", cursor="hand2")
    close_btn.pack()
    
    error_root.mainloop()
    sys.exit(1)

# ---------- ИМПОРТ БИБЛИОТЕК ----------
try:
    import pandas as pd
    import requests
    import urllib3
    try:
        from PIL import Image, ImageTk
    except ImportError:
        try:
            import PIL
            from PIL import Image, ImageTk
        except ImportError:
            class ImageTkStub:
                @staticmethod
                def PhotoImage(*args, **kwargs):
                    return None
            Image = None
            ImageTk = ImageTkStub()
            print("⚠️ Pillow не установлен.")
except ImportError as e:
    error_root = tk.Tk()
    error_root.title("Ошибка импорта")
    error_root.geometry("600x350")
    error_root.configure(bg='#f5f5f7')
    
    title_label = tk.Label(error_root, text="❌ ОШИБКА ИМПОРТА БИБЛИОТЕК", 
                          font=("Segoe UI", 14, "bold"), bg='#f5f5f7', fg='#e74c3c')
    title_label.pack(pady=(20, 10))
    
    error_text = scrolledtext.ScrolledText(error_root, wrap=tk.WORD, 
                                           font=("Consolas", 10), bg='#ffffff',
                                           fg='#1a1a2e', relief="flat", bd=1,
                                           padx=10, pady=10)
    error_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    error_text.insert(tk.END, f"❌ Не удалось импортировать библиотеку:\n\n{str(e)}\n\n")
    error_text.insert(tk.END, "🔧 РЕШЕНИЕ:\n\n")
    error_text.insert(tk.END, "1. Перезапустите программу\n")
    error_text.insert(tk.END, "2. Установите библиотеки вручную:\n")
    for lib in installer.required_libs.keys():
        error_text.insert(tk.END, f"   pip install {lib}\n")
    
    error_text.config(state=tk.DISABLED)
    
    btn_frame = tk.Frame(error_root, bg='#f5f5f7')
    btn_frame.pack(pady=10)
    
    close_btn = tk.Button(btn_frame, text="Закрыть", command=error_root.destroy,
                         font=("Segoe UI", 11), bg="#e74c3c", fg="white",
                         padx=30, pady=8, relief="flat", cursor="hand2")
    close_btn.pack()
    
    error_root.mainloop()
    sys.exit(1)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ---------- КЛАСС ДЛЯ РАБОТЫ С PERCo-Web API ----------
class PERCoAPI:
    def __init__(self, base_url, username, password):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.verify = False
        self.token = None
        self.token_expiry = None
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        self.last_response = None
        self.last_error = None
        
    def login(self):
        try:
            auth_paths = [
                '/api/system/auth',
                '/system/auth',
                '/api/auth/login',
                '/auth/login'
            ]
            
            data = {"login": self.username, "password": self.password}
            
            for auth_path in auth_paths:
                url = f"{self.base_url}{auth_path}"
                try:
                    print(f"Попытка авторизации: {url}")
                    response = self.session.post(url, json=data, headers=self.headers, timeout=15)
                    self.last_response = response
                    
                    if response.status_code == 200:
                        try:
                            result = response.json()
                            if 'token' in result:
                                self.token = result['token']
                                self.session.headers.update({
                                    'Authorization': f'Bearer {self.token}'
                                })
                                self.token_expiry = datetime.now() + timedelta(hours=1)
                                print(f"✅ Успешная авторизация через {url}")
                                return True, "Успешная авторизация"
                        except json.JSONDecodeError:
                            continue
                except Exception as e:
                    print(f"Ошибка при запросе к {url}: {e}")
                    continue
            
            if self.last_response:
                return False, f"Ошибка авторизации: {self.last_response.status_code}"
            else:
                return False, "Не удалось подключиться к серверу"
                
        except Exception as e:
            return False, f"Ошибка: {str(e)}"
    
    def _ensure_token(self):
        if not self.token or (self.token_expiry and datetime.now() >= self.token_expiry):
            success, message = self.login()
            if not success:
                raise Exception(f"Не удалось обновить токен: {message}")
        return self.token
    
    def get_staff_list(self, status='active', search=''):
        try:
            self._ensure_token()
            
            params = {"status": status}
            if search:
                params['search'] = search
            
            print(f"Запрос сотрудников (fullList):")
            
            urls = [
                f"{self.base_url}/api/users/staff/fullList",
                f"{self.base_url}/users/staff/fullList",
                f"{self.base_url}/api/users/staff/list",
                f"{self.base_url}/users/staff/list"
            ]
            
            for url in urls:
                try:
                    print(f"  >> Пробую: {url}")
                    response = self.session.get(url, params=params, timeout=30)
                    self.last_response = response
                    
                    if response.status_code == 200:
                        try:
                            return True, response.json()
                        except json.JSONDecodeError:
                            continue
                    elif response.status_code == 404:
                        continue
                    else:
                        return False, f"{response.status_code} - {response.text[:200]}"
                except Exception as e:
                    continue
            
            return False, "Не удалось получить список сотрудников"
                
        except Exception as e:
            return False, str(e)
    
    def get_access_events(self, start_date=None, end_date=None, person_id=None, limit=10000):
        try:
            self._ensure_token()
            
            params = {"limit": limit}
            
            if start_date:
                params['dateBegin'] = start_date.strftime('%Y-%m-%d')
            if end_date:
                params['dateEnd'] = end_date.strftime('%Y-%m-%d')
            if person_id:
                params['personId'] = person_id
            
            print(f"Запрос событий (Отчет о проходах):")
            print(f"Параметры: {params}")
            
            urls = [
                f"{self.base_url}/api/accessReports/events",
                f"{self.base_url}/accessReports/events",
                f"{self.base_url}/api/access/events",
                f"{self.base_url}/access/events"
            ]
            
            for url in urls:
                try:
                    print(f"  >> Пробую: {url}")
                    response = self.session.get(url, params=params, timeout=60)
                    self.last_response = response
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            print(f"  >> Получен ответ: {type(data)}")
                            
                            if isinstance(data, dict) and 'rows' in data:
                                rows = data['rows']
                                print(f"  >> Найдено записей: {len(rows)}")
                                return True, rows
                            elif isinstance(data, list):
                                print(f"  >> Найдено записей: {len(data)}")
                                return True, data
                            elif isinstance(data, dict) and 'items' in data:
                                items = data['items']
                                print(f"  >> Найдено записей: {len(items)}")
                                return True, items
                            elif data:
                                print(f"  >> Найдено 1 запись")
                                return True, [data] if data else []
                            else:
                                print(f"  >> Пустой ответ")
                                return True, []
                        except json.JSONDecodeError as e:
                            print(f"  >> Ошибка парсинга JSON: {e}")
                            continue
                    elif response.status_code == 404:
                        print(f"  >> URL не найден (404)")
                        continue
                    else:
                        print(f"  >> Ошибка {response.status_code}")
                        continue
                except Exception as e:
                    print(f"  >> Ошибка: {e}")
                    continue
            
            return False, "Не удалось получить события доступа"
                
        except Exception as e:
            return False, str(e)
    
    def get_staff_by_id(self, staff_id):
        try:
            self._ensure_token()
            
            urls = [
                f"{self.base_url}/api/users/staff/{staff_id}",
                f"{self.base_url}/users/staff/{staff_id}"
            ]
            
            for url in urls:
                try:
                    response = self.session.get(url, timeout=30)
                    if response.status_code == 200:
                        try:
                            return True, response.json()
                        except json.JSONDecodeError:
                            continue
                except:
                    continue
            
            return False, "Не удалось получить данные сотрудника"
                
        except Exception as e:
            return False, str(e)

# ---------- ЛОГИКА РАСЧЕТА ----------
def process_data_from_api(events, object_name="ЗИФ"):
    processed_data = []
    
    print(f"Обработка {len(events)} событий...")
    
    for event in events:
        if not isinstance(event, dict):
            continue
        
        try:
            event_time = None
            time_fields = ['time_label', 'eventTime', 'time', 'dateTime', 'timestamp']
            for field in time_fields:
                if field in event:
                    value = event[field]
                    if isinstance(value, str):
                        formats = [
                            '%Y-%m-%dT%H:%M:%S',
                            '%Y-%m-%d %H:%M:%S',
                            '%d.%m.%Y %H:%M:%S',
                            '%Y-%m-%dT%H:%M:%S.%f',
                            '%Y-%m-%dT%H:%M:%S.%fZ'
                        ]
                        for fmt in formats:
                            try:
                                event_time = datetime.strptime(value, fmt)
                                break
                            except:
                                continue
                    elif isinstance(value, (int, float)):
                        event_time = datetime.fromtimestamp(value / 1000)
                    if event_time:
                        break
            
            if not event_time:
                continue
            
            person_name = event.get('fio', '')
            if not person_name:
                if 'person' in event and isinstance(event['person'], dict):
                    person = event['person']
                    parts = []
                    for f in ['last_name', 'firstName', 'name', 'lastName']:
                        if f in person and person[f]:
                            parts.append(str(person[f]))
                    if 'middle_name' in person and person['middle_name']:
                        parts.append(str(person['middle_name']))
                    person_name = ' '.join(parts) if parts else ''
                elif 'personName' in event:
                    person_name = event['personName']
                elif 'fullName' in event:
                    person_name = event['fullName']
            
            if not person_name:
                continue
            
            person_id = event.get('user_id', '')
            if not person_id:
                person_id = event.get('personId', '')
            if not person_id:
                person_id = event.get('id', '')
            
            zone_exit = event.get('zone_exit', '')
            zone_enter = event.get('zone_enter', '')
            
            if not zone_exit and 'zone_exit_id' in event:
                zone_exit = f"Зона {event.get('zone_exit_id', '')}"
            if not zone_enter and 'zone_enter_id' in event:
                zone_enter = f"Зона {event.get('zone_enter_id', '')}"
            
            if not zone_exit and not zone_enter:
                place = event.get('place', '')
                if place:
                    zone_enter = place
            
            # Проверяем, относится ли событие к объекту
            is_exit = object_name in zone_exit or zone_exit == 'АБК ЗИФ' or 'АБК' in zone_exit
            is_entry = object_name in zone_enter or zone_enter == 'АБК ЗИФ' or 'АБК' in zone_enter
            
            if is_exit:
                from_place = zone_exit if zone_exit else 'АБК ЗИФ'
                to_place = 'Неконтролируемая территория'
                processed_data.append({
                    'datetime': event_time,
                    'from_place': from_place,
                    'to_place': to_place,
                    'person_name': person_name,
                    'person_id': str(person_id) if person_id else '',
                    'zone_exit': zone_exit,
                    'zone_enter': zone_enter,
                    'direction': 'exit'
                })
            elif is_entry:
                from_place = 'Неконтролируемая территория'
                to_place = zone_enter if zone_enter else 'АБК ЗИФ'
                processed_data.append({
                    'datetime': event_time,
                    'from_place': from_place,
                    'to_place': to_place,
                    'person_name': person_name,
                    'person_id': str(person_id) if person_id else '',
                    'zone_exit': zone_exit,
                    'zone_enter': zone_enter,
                    'direction': 'entry'
                })
            elif zone_exit or zone_enter:
                processed_data.append({
                    'datetime': event_time,
                    'from_place': zone_exit if zone_exit else 'Неконтролируемая территория',
                    'to_place': zone_enter if zone_enter else 'АБК ЗИФ',
                    'person_name': person_name,
                    'person_id': str(person_id) if person_id else '',
                    'zone_exit': zone_exit,
                    'zone_enter': zone_enter,
                    'direction': 'unknown'
                })
            
        except Exception as e:
            print(f"  >> Ошибка обработки события: {e}")
            continue
    
    print(f"Обработано записей: {len(processed_data)}")
    return processed_data

def load_excel(file_path):
    try:
        df = pd.read_excel(file_path, header=0)
        df.dropna(how='all', inplace=True)
        return df
    except Exception as e:
        return None

def process_data_from_excel(df, object_name="ЗИФ"):
    processed_data = []
    
    required_cols = ['Фамилия', 'Имя', 'Отчество', 'Дата', 'Выход из', 'Вход в']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        return None, f"Отсутствуют колонки: {', '.join(missing_cols)}"
    
    df = df.copy()
    df['datetime'] = pd.to_datetime(df['Дата'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['datetime'])
    
    df['person_name'] = df['Фамилия'] + ' ' + df['Имя'] + ' ' + df.get('Отчество', '')
    df['person_id'] = df.get('Табельный номер', '')
    
    df_filtered = df[
        ((df['Вход в'] == f'АБК {object_name}') | (df['Вход в'].str.contains(object_name, case=False, na=False))) |
        ((df['Выход из'] == f'АБК {object_name}') | (df['Выход из'].str.contains(object_name, case=False, na=False)))
    ]
    
    if df_filtered.empty:
        return None, "Нет данных для указанного объекта"
    
    for _, row in df_filtered.iterrows():
        processed_data.append({
            'datetime': row['datetime'],
            'from_place': row['Выход из'],
            'to_place': row['Вход в'],
            'person_name': row['person_name'],
            'person_id': str(row['person_id']) if row['person_id'] else '',
            'zone_exit': row['Выход из'],
            'zone_enter': row['Вход в']
        })
    
    return processed_data, None

def calculate_intervals(person_data, entrance_from, entrance_to, exit_from, exit_to):
    intervals = []
    active_start = None
    
    person_data = sorted(person_data, key=lambda x: x['datetime'])
    
    for event in person_data:
        dt = event['datetime']
        from_place = str(event['from_place']).strip()
        to_place = str(event['to_place']).strip()
        
        if from_place == entrance_from and to_place == entrance_to:
            if active_start is None:
                active_start = dt
            else:
                intervals.append((active_start, dt))
                active_start = dt
        elif from_place == exit_from and to_place == exit_to:
            if active_start is not None:
                intervals.append((active_start, dt))
                active_start = None
    
    return intervals

def split_intervals_by_day(intervals):
    daily = defaultdict(float)
    for start, end in intervals:
        if start.date() == end.date():
            daily[start.date()] += (end - start).total_seconds() / 60.0
        else:
            current = start
            while current.date() < end.date():
                next_midnight = datetime(current.year, current.month, current.day, 0, 0, 0) + timedelta(days=1)
                part_end = min(next_midnight, end)
                delta = (part_end - current).total_seconds() / 60.0
                daily[current.date()] += delta
                current = next_midnight
    return dict(daily)

def format_time_seconds(minutes):
    total_seconds = int(round(minutes * 60))
    hours = total_seconds // 3600
    minutes_rem = (total_seconds % 3600) // 60
    seconds_rem = total_seconds % 60
    return f"{hours} ч {minutes_rem} мин {seconds_rem} сек"

def calculate_results(data, norm_hours, object_name="ЗИФ", selected_employee=None):
    """
    Расчет результатов с фильтрацией по выбранному сотруднику
    """
    entrance_from = f"АБК {object_name}"
    entrance_to = "Неконтролируемая территория"
    exit_from = "Неконтролируемая территория"
    exit_to = f"АБК {object_name}"
    
    entrance_from_alt = "АБК ЗИФ"
    entrance_to_alt = object_name
    exit_from_alt = object_name
    exit_to_alt = "АБК ЗИФ"
    
    employees = defaultdict(list)
    for event in data:
        key = f"{event['person_name']}|{event.get('person_id', '')}"
        employees[key].append(event)
    
    results = {}
    
    for key, events in employees.items():
        name_parts = key.split('|')
        person_name = name_parts[0]
        person_id = name_parts[1] if len(name_parts) > 1 else ''
        
        # Фильтр по выбранному сотруднику
        if selected_employee and person_name != selected_employee:
            continue
        
        intervals = calculate_intervals(events, entrance_from, entrance_to, exit_from, exit_to)
        
        if not intervals:
            intervals = calculate_intervals(events, entrance_from_alt, entrance_to_alt, exit_from_alt, exit_to_alt)
        
        if not intervals and events:
            for event in events:
                if event.get('direction') == 'entry':
                    intervals.append((event['datetime'], event['datetime'] + timedelta(minutes=1)))
                elif event.get('direction') == 'exit':
                    intervals.append((event['datetime'] - timedelta(minutes=1), event['datetime']))
        
        if not intervals:
            continue
        
        daily = split_intervals_by_day(intervals)
        total_minutes = sum(daily.values())
        
        results[person_id] = {
            'fio': person_name,
            'daily': daily,
            'total_minutes': total_minutes
        }
    
    return results

def generate_report(results, norm_hours, object_name="ЗИФ"):
    norm_minutes = norm_hours * 60.0
    
    output_lines = []
    output_lines.append("="*80)
    output_lines.append(f">>> ОТЧЁТ: ВРЕМЯ ПРИСУТСТВИЯ НА {object_name} <<<")
    output_lines.append(f"📅 Норма: {norm_hours:.2f} часов в месяц")
    output_lines.append("="*80)
    
    if not results:
        output_lines.append("\n❌ Нет данных для отображения")
        return output_lines
    
    for emp_id, data in results.items():
        fio = data['fio']
        daily = data['daily']
        total_minutes = data['total_minutes']
        total_hours = total_minutes / 60.0
        percent = (total_minutes / norm_minutes) * 100.0 if norm_minutes > 0 else 0.0
        
        output_lines.append(f"\n👤 Сотрудник: {fio} (Таб. № {emp_id})")
        
        if not daily:
            output_lines.append("   📭 Нет записей.")
            output_lines.append(f"   ⏱️ Общее время: 0 ч 0 мин 0 сек")
            output_lines.append(f"   📈 Процент от нормы: 0.0000%")
            continue
        
        output_lines.append(f"   📅 {'Дата':<12} ⏱️ {'Время на объекте':<30}")
        output_lines.append(f"   {'-'*12} {'-'*30}")
        
        for date in sorted(daily.keys()):
            mins = daily[date]
            output_lines.append(f"   {date.strftime('%d.%m.%Y'):<12} {format_time_seconds(mins):<30}")
        
        output_lines.append(f"\n   🕒 Общее время: {format_time_seconds(total_minutes)}")
        output_lines.append(f"   ⌛ Всего часов: {total_hours:.2f} ч")
        output_lines.append(f"   📊 Процент от нормы ({norm_hours:.2f} ч): {percent:.4f}%")
        output_lines.append("")
    
    output_lines.append("="*80)
    return output_lines

def save_report_to_file_auto(output_lines, script_dir):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_name = os.path.join(script_dir, f"report_{timestamp}.txt")
    try:
        with open(report_name, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines))
        return report_name
    except:
        return None

def save_report_to_path(output_lines, filepath):
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines))
        return True
    except:
        return False

# ---------- КЛАССЫ ДЛЯ ПОЛЕЙ С КОПИРОВАНИЕМ ----------
class CopyableEntry(tk.Entry):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.bind('<Control-c>', self.copy)
        self.bind('<Control-v>', self.paste)
        self.bind('<Control-x>', self.cut)
        self.bind('<Control-a>', self.select_all)
        self.bind('<Button-3>', self.show_context_menu)
        self.context_menu = None
    
    def copy(self, event=None):
        self.clipboard_clear()
        if self.selection_present():
            self.clipboard_append(self.selection_get())
        return "break"
    
    def paste(self, event=None):
        try:
            text = self.clipboard_get()
            self.insert(tk.INSERT, text)
        except:
            pass
        return "break"
    
    def cut(self, event=None):
        self.copy()
        self.delete(tk.SEL_FIRST, tk.SEL_LAST)
        return "break"
    
    def select_all(self, event=None):
        self.select_range(0, tk.END)
        self.icursor(tk.END)
        return "break"
    
    def show_context_menu(self, event):
        if self.context_menu is None:
            self.context_menu = tk.Menu(self, tearoff=0)
            self.context_menu.add_command(label="Копировать", command=lambda: self.copy())
            self.context_menu.add_command(label="Вставить", command=lambda: self.paste())
            self.context_menu.add_command(label="Вырезать", command=lambda: self.cut())
            self.context_menu.add_separator()
            self.context_menu.add_command(label="Выделить всё", command=lambda: self.select_all())
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

class CopyableCombobox(ttk.Combobox):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.bind('<Control-c>', self.copy)
        self.bind('<Control-v>', self.paste)
        self.bind('<Control-x>', self.cut)
        self.bind('<Control-a>', self.select_all)
        self.bind('<Button-3>', self.show_context_menu)
        self.context_menu = None
    
    def copy(self, event=None):
        self.clipboard_clear()
        self.clipboard_append(self.get())
        return "break"
    
    def paste(self, event=None):
        try:
            text = self.clipboard_get()
            self.set(text)
            self.event_generate('<<ComboboxSelected>>')
        except:
            pass
        return "break"
    
    def cut(self, event=None):
        self.copy()
        self.set('')
        return "break"
    
    def select_all(self, event=None):
        self.select_range(0, tk.END)
        self.icursor(tk.END)
        return "break"
    
    def show_context_menu(self, event):
        if self.context_menu is None:
            self.context_menu = tk.Menu(self, tearoff=0)
            self.context_menu.add_command(label="Копировать", command=lambda: self.copy())
            self.context_menu.add_command(label="Вставить", command=lambda: self.paste())
            self.context_menu.add_command(label="Вырезать", command=lambda: self.cut())
            self.context_menu.add_separator()
            self.context_menu.add_command(label="Выделить всё", command=lambda: self.select_all())
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

class CopyableLabel(tk.Label):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.bind('<Control-c>', self.copy)
        self.bind('<Button-3>', self.show_context_menu)
        self.context_menu = None
        self.cursor = "hand2"
    
    def copy(self, event=None):
        text = self.cget('text')
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)
        return "break"
    
    def show_context_menu(self, event):
        if self.context_menu is None:
            self.context_menu = tk.Menu(self, tearoff=0)
            self.context_menu.add_command(label="Копировать текст", command=lambda: self.copy())
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

# ---------- ОСНОВНОЕ ПРИЛОЖЕНИЕ ----------
class ModernApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{PROGRAM_NAME} v{VERSION}")
        self.root.geometry("1400x1000")
        self.root.resizable(True, True)
        self.root.minsize(1000, 800)
        
        # Цветовая палитра
        self.colors = {
            'bg': '#f0f2f5',
            'fg': '#1a1a2e',
            'accent': '#4361ee',
            'accent_hover': '#3a56d4',
            'accent_light': '#e8edfd',
            'card_bg': '#ffffff',
            'border': '#e0e0e0',
            'secondary': '#6c757d',
            'success': '#2ecc71',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'purple': '#8e44ad',
            'teal': '#1abc9c'
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        # Шрифты
        try:
            self.title_font = font.Font(family="Segoe UI", size=22, weight="bold")
            self.heading_font = font.Font(family="Segoe UI", size=14, weight="bold")
            self.body_font = font.Font(family="Segoe UI", size=10)
            self.mono_font = font.Font(family="Consolas", size=10)
        except:
            self.title_font = font.Font(family="Arial", size=22, weight="bold")
            self.heading_font = font.Font(family="Arial", size=14, weight="bold")
            self.body_font = font.Font(family="Arial", size=10)
            self.mono_font = font.Font(family="Courier New", size=10)
        
        # Переменные
        self.api = None
        self.is_connected = False
        self.staff_data = {}
        self.employee_data = {}
        self.room_objects = []
        self.current_report = None
        self.current_report_text = None
        self.processing = False
        self.connection_status = "disconnected"
        self.all_employees = []
        self.employee_list = []
        self.search_timer = None
        
        # Создание интерфейса
        self.create_widgets()
        
        # Глобальные горячие клавиши для копирования/вставки
        self.root.bind('<Control-c>', self.global_copy)
        self.root.bind('<Control-v>', self.global_paste)
    
    def global_copy(self, event):
        """Глобальное копирование из фокусированного виджета"""
        widget = self.root.focus_get()
        if hasattr(widget, 'copy'):
            widget.copy()
        return "break"
    
    def global_paste(self, event):
        """Глобальная вставка в фокусированный виджет"""
        widget = self.root.focus_get()
        if hasattr(widget, 'paste'):
            widget.paste()
        return "break"
    
    def copy_text_selection(self, event=None):
        """Копирование выделенного текста из ScrolledText"""
        try:
            widget = self.root.focus_get()
            if hasattr(widget, 'selection_get'):
                text = widget.selection_get()
                if text:
                    self.root.clipboard_clear()
                    self.root.clipboard_append(text)
        except:
            pass
        return "break" if event else None
    
    def select_all_text(self, event=None):
        """Выделение всего текста в ScrolledText"""
        try:
            widget = self.root.focus_get()
            if hasattr(widget, 'tag_add'):
                widget.tag_add(tk.SEL, "1.0", tk.END)
                widget.mark_set(tk.INSERT, "1.0")
                widget.see(tk.INSERT)
        except:
            pass
        return "break" if event else None
    
    def show_text_context_menu(self, event):
        """Контекстное меню для текстового поля"""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Копировать", command=self.copy_text_selection)
        menu.add_command(label="Выделить всё", command=self.select_all_text)
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def create_widgets(self):
        # Основной контейнер
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Верхняя панель с заголовком
        header_frame = tk.Frame(main_container, bg=self.colors['card_bg'], relief="flat", bd=1)
        header_frame.pack(fill=tk.X, pady=(0, 12))
        
        title_inner = tk.Frame(header_frame, bg=self.colors['card_bg'])
        title_inner.pack(fill=tk.X, padx=20, pady=15)
        
        self.title_label = CopyableLabel(title_inner, text="🔐 PERCo-Web Аналитик", 
                                        font=self.title_font, bg=self.colors['card_bg'], 
                                        fg=self.colors['accent'])
        self.title_label.pack(side=tk.LEFT)
        
        version_label = CopyableLabel(title_inner, text=f"v{VERSION}", font=self.body_font, 
                                     bg=self.colors['card_bg'], fg=self.colors['secondary'])
        version_label.pack(side=tk.LEFT, padx=(8,0))
        
        author_frame = tk.Frame(title_inner, bg=self.colors['card_bg'])
        author_frame.pack(side=tk.RIGHT)
        
        author_label = CopyableLabel(author_frame, text=AUTHOR, font=self.body_font, 
                                    bg=self.colors['card_bg'], fg=self.colors['secondary'])
        author_label.pack(side=tk.RIGHT)
        
        # Основная сетка
        content_frame = tk.Frame(main_container, bg=self.colors['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Левая панель - Настройки
        left_panel = tk.Frame(content_frame, bg=self.colors['bg'], width=600)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 12))
        left_panel.pack_propagate(False)
        
        # Правая панель - Результаты
        right_panel = tk.Frame(content_frame, bg=self.colors['bg'])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # ---------- ЛЕВАЯ ПАНЕЛЬ ----------
        # Карточка подключения к API
        api_card = self.create_card(left_panel, "🌐 Подключение к PERCo-Web")
        
        fields_frame = tk.Frame(api_card, bg=self.colors['card_bg'])
        fields_frame.pack(fill=tk.X, padx=15, pady=(5, 10))
        
        self.create_copyable_entry(fields_frame, "Адрес сервера:", "", 0)
        self.create_copyable_entry(fields_frame, "Логин:", "", 1)
        self.create_copyable_entry(fields_frame, "Пароль:", "", 2, show="•")
        
        btn_frame = tk.Frame(api_card, bg=self.colors['card_bg'])
        btn_frame.pack(fill=tk.X, padx=15, pady=(0, 12))
        
        self.connect_btn = self.create_button(btn_frame, "🔗 Подключиться", self.connect_api, 
                                             self.colors['accent'], "left")
        self.disconnect_btn = self.create_button(btn_frame, "🔌 Отключиться", self.disconnect_api,
                                                self.colors['danger'], "left", state=tk.DISABLED)
        
        self.status_indicator = CopyableLabel(btn_frame, text="● Отключено", 
                                             font=self.body_font, bg=self.colors['card_bg'], 
                                             fg=self.colors['danger'])
        self.status_indicator.pack(side=tk.RIGHT, padx=5)
        
        # Разделитель
        ttk.Separator(left_panel, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # Карточка параметров
        params_card = self.create_card(left_panel, "⚙️ Параметры расчета")
        
        params_frame = tk.Frame(params_card, bg=self.colors['card_bg'])
        params_frame.pack(fill=tk.X, padx=15, pady=(5, 12))
        
        # Объект
        obj_frame = tk.Frame(params_frame, bg=self.colors['card_bg'])
        obj_frame.pack(fill=tk.X, pady=3)
        obj_label = CopyableLabel(obj_frame, text="Объект (помещение):", font=self.body_font, 
                                 bg=self.colors['card_bg'], width=17, anchor='w')
        obj_label.pack(side=tk.LEFT)
        
        self.object_var = tk.StringVar()
        self.object_combo = CopyableCombobox(obj_frame, textvariable=self.object_var,
                                            width=30, state='readonly')
        self.object_combo.pack(side=tk.LEFT, padx=5)
        self.object_combo['values'] = []
        
        self.refresh_objects_btn = tk.Button(obj_frame, text="🔄 Обновить объекты", 
                                            command=self.load_objects_from_data,
                                            font=self.body_font, bg=self.colors['accent'],
                                            fg="white", padx=10, pady=2,
                                            relief="flat", cursor="hand2", bd=0, state=tk.DISABLED)
        self.refresh_objects_btn.pack(side=tk.LEFT, padx=5)
        
        # Норма
        norm_frame = tk.Frame(params_frame, bg=self.colors['card_bg'])
        norm_frame.pack(fill=tk.X, pady=3)
        norm_label = CopyableLabel(norm_frame, text="Норма (часы):", font=self.body_font, 
                                  bg=self.colors['card_bg'], width=17, anchor='w')
        norm_label.pack(side=tk.LEFT)
        
        self.norm_var = tk.StringVar(value="140")
        self.norm_entry = CopyableEntry(norm_frame, textvariable=self.norm_var, font=self.body_font,
                                       bg=self.colors['card_bg'], relief="solid", bd=1, width=10)
        self.norm_entry.pack(side=tk.LEFT, padx=5)
        
        # Период
        period_frame = tk.Frame(params_frame, bg=self.colors['card_bg'])
        period_frame.pack(fill=tk.X, pady=3)
        period_label = CopyableLabel(period_frame, text="Период:", font=self.body_font, 
                                    bg=self.colors['card_bg'], width=17, anchor='w')
        period_label.pack(side=tk.LEFT)
        
        self.period_var = tk.StringVar(value="Текущий месяц")
        self.period_combo = CopyableCombobox(period_frame, textvariable=self.period_var,
                                            values=['Текущий месяц', 'Прошлый месяц', 'За последние 30 дней', 
                                                   'За последние 7 дней', 'Вчера', 'Сегодня',
                                                   'Произвольный'],
                                            width=25, state='readonly')
        self.period_combo.pack(side=tk.LEFT, padx=5)
        self.period_combo.bind('<<ComboboxSelected>>', self.on_period_change)
        
        # Дата для произвольного периода
        self.date_frame = tk.Frame(params_frame, bg=self.colors['card_bg'])
        self.date_frame.pack(fill=tk.X, pady=3)
        self.date_frame.pack_forget()
        
        date_inner = tk.Frame(self.date_frame, bg=self.colors['card_bg'])
        date_inner.pack(side=tk.LEFT, padx=17)
        
        date_label_from = CopyableLabel(date_inner, text="С:", font=self.body_font, 
                                       bg=self.colors['card_bg'])
        date_label_from.pack(side=tk.LEFT)
        
        self.start_date_var = tk.StringVar()
        self.start_date_entry = CopyableEntry(date_inner, textvariable=self.start_date_var, font=self.body_font,
                                             bg=self.colors['card_bg'], relief="solid", bd=1, width=12)
        self.start_date_entry.pack(side=tk.LEFT, padx=3)
        
        date_label_to = CopyableLabel(date_inner, text="По:", font=self.body_font, 
                                     bg=self.colors['card_bg'])
        date_label_to.pack(side=tk.LEFT, padx=(10,3))
        
        self.end_date_var = tk.StringVar()
        self.end_date_entry = CopyableEntry(date_inner, textvariable=self.end_date_var, font=self.body_font,
                                           bg=self.colors['card_bg'], relief="solid", bd=1, width=12)
        self.end_date_entry.pack(side=tk.LEFT, padx=3)
        
        # Сотрудник
        emp_frame = tk.Frame(params_frame, bg=self.colors['card_bg'])
        emp_frame.pack(fill=tk.X, pady=3)
        emp_label = CopyableLabel(emp_frame, text="Сотрудник (персонал):", font=self.body_font, 
                                 bg=self.colors['card_bg'], width=17, anchor='w')
        emp_label.pack(side=tk.LEFT)
        
        search_frame = tk.Frame(emp_frame, bg=self.colors['card_bg'])
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.employee_var = tk.StringVar()
        self.employee_combo = CopyableCombobox(search_frame, textvariable=self.employee_var,
                                              width=30, state='normal')
        self.employee_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.employee_combo.set('')
        self.employee_combo['values'] = []
        
        self.employee_combo.bind('<KeyRelease>', self.on_employee_search)
        self.employee_combo.bind('<<ComboboxSelected>>', self.on_employee_select)
        self.employee_combo.bind('<FocusIn>', self.on_employee_focus)
        
        self.load_staff_btn = tk.Button(search_frame, text="📥 Загрузить персонал", 
                                       command=self.load_staff_list,
                                       font=self.body_font, bg=self.colors['accent'],
                                       fg="white", padx=10, pady=2,
                                       relief="flat", cursor="hand2", bd=0, state=tk.DISABLED)
        self.load_staff_btn.pack(side=tk.RIGHT, padx=2)
        
        # Кнопки действий
        action_btn_frame = tk.Frame(left_panel, bg=self.colors['bg'])
        action_btn_frame.pack(fill=tk.X, pady=8)
        
        self.load_events_btn = self.create_button(action_btn_frame, "📥 Загрузить события из PERCo", 
                                                 self.load_from_api,
                                                 self.colors['teal'], "left", size=14, state=tk.DISABLED)
        self.run_btn = self.create_button(action_btn_frame, "🚀 Рассчитать", self.run_calculation,
                                         self.colors['success'], "left", size=14)
        self.clear_btn = self.create_button(action_btn_frame, "🧹 Очистить", self.clear_output,
                                           self.colors['secondary'], "left", size=12)
        self.copy_btn = self.create_button(action_btn_frame, "📋 Копировать", self.copy_to_clipboard,
                                          self.colors['purple'], "left", size=12)
        self.save_btn = self.create_button(action_btn_frame, "💾 Сохранить", self.save_report_dialog,
                                          self.colors['accent'], "left", size=12, state=tk.DISABLED)
        
        # Загрузка из Excel
        excel_frame = tk.Frame(left_panel, bg=self.colors['bg'])
        excel_frame.pack(fill=tk.X, pady=5)
        
        excel_label = CopyableLabel(excel_frame, text="Или загрузите из Excel:", font=self.body_font, 
                                   bg=self.colors['bg'])
        excel_label.pack(side=tk.LEFT)
        
        self.file_path_var = tk.StringVar()
        self.file_entry = CopyableEntry(excel_frame, textvariable=self.file_path_var, font=self.body_font,
                                       bg=self.colors['card_bg'], relief="solid", bd=1, width=30)
        self.file_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(excel_frame, text="📂 Обзор", command=self.select_file,
                 font=self.body_font, bg=self.colors['accent'], fg="white", 
                 padx=10, pady=2, relief="flat", cursor="hand2", bd=0).pack(side=tk.LEFT, padx=2)
        
        self.load_excel_btn = tk.Button(excel_frame, text="📥 Загрузить Excel", 
                                       command=self.load_from_excel,
                                       font=self.body_font, bg=self.colors['teal'],
                                       fg="white", padx=10, pady=2,
                                       relief="flat", cursor="hand2", bd=0)
        self.load_excel_btn.pack(side=tk.LEFT, padx=2)
        
        # Статус
        status_frame = tk.Frame(left_panel, bg=self.colors['bg'])
        status_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.status_var = tk.StringVar(value="✅ Готов")
        self.status_label = CopyableLabel(status_frame, textvariable=self.status_var, 
                                         font=self.body_font, bg=self.colors['bg'], 
                                         fg=self.colors['success'])
        self.status_label.pack(side=tk.LEFT)
        
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate', length=150)
        self.progress.pack(side=tk.RIGHT)
        
        # ---------- ПРАВАЯ ПАНЕЛЬ ----------
        notebook = ttk.Notebook(right_panel)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Вкладка "Отчет"
        report_tab = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(report_tab, text="📄 Отчет")
        
        self.output_text = scrolledtext.ScrolledText(report_tab, wrap=tk.WORD, font=self.mono_font,
                                                     bg=self.colors['card_bg'], fg=self.colors['fg'], 
                                                     relief="flat", bd=0, padx=15, pady=10, 
                                                     highlightthickness=1, highlightcolor=self.colors['border'],
                                                     selectbackground=self.colors['accent'], 
                                                     selectforeground="white")
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Настройка горячих клавиш для текстового поля
        self.output_text.bind('<Control-c>', self.copy_text_selection)
        self.output_text.bind('<Control-a>', self.select_all_text)
        self.output_text.bind('<Button-3>', self.show_text_context_menu)
        
        # Цветные теги
        self.output_text.tag_configure("good", foreground=self.colors['success'], 
                                      font=(self.mono_font, 10, "bold"))
        self.output_text.tag_configure("warning", foreground=self.colors['warning'], 
                                      font=(self.mono_font, 10, "bold"))
        self.output_text.tag_configure("bad", foreground=self.colors['danger'], 
                                      font=(self.mono_font, 10, "bold"))
        self.output_text.tag_configure("header", foreground=self.colors['accent'], 
                                      font=(self.mono_font, 10, "bold"))
        self.output_text.tag_configure("date", foreground=self.colors['purple'], 
                                      font=(self.mono_font, 9))
        self.output_text.tag_configure("time", foreground=self.colors['teal'], 
                                      font=(self.mono_font, 9))
        self.output_text.tag_configure("emoji", foreground=self.colors['accent'], 
                                      font=(self.mono_font, 10))
        
        # Вкладка "Информация"
        info_tab = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(info_tab, text="👤 Информация")
        
        info_content = tk.Frame(info_tab, bg=self.colors['bg'])
        info_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        self.info_text = scrolledtext.ScrolledText(info_content, wrap=tk.WORD, font=self.body_font,
                                                   bg=self.colors['card_bg'], fg=self.colors['fg'],
                                                   relief="flat", bd=0, padx=15, pady=10,
                                                   highlightthickness=1, highlightcolor=self.colors['border'])
        self.info_text.pack(fill=tk.BOTH, expand=True)
        self.info_text.insert(tk.END, "Выберите сотрудника для просмотра информации")
        self.info_text.config(state=tk.DISABLED)
        
        self.info_text.bind('<Control-c>', self.copy_text_selection)
        self.info_text.bind('<Control-a>', self.select_all_text)
        self.info_text.bind('<Button-3>', self.show_text_context_menu)
        
        # Статус внизу
        bottom_frame = tk.Frame(main_container, bg=self.colors['bg'])
        bottom_frame.pack(fill=tk.X, pady=(10, 0))
        
        bottom_label = CopyableLabel(bottom_frame, text=f"🔧 {AUTHOR} | {LICENSE} | GitHub: {GITHUB}", 
                                    font=self.body_font, bg=self.colors['bg'], fg=self.colors['secondary'])
        bottom_label.pack(side=tk.LEFT)
        
        self.connection_info = CopyableLabel(bottom_frame, text="", font=self.body_font, 
                                            bg=self.colors['bg'], fg=self.colors['secondary'])
        self.connection_info.pack(side=tk.RIGHT)
    
    def create_card(self, parent, title):
        card = tk.Frame(parent, bg=self.colors['card_bg'], relief="flat", bd=1)
        card.pack(fill=tk.X, pady=4)
        
        header = tk.Frame(card, bg=self.colors['accent_light'])
        header.pack(fill=tk.X)
        
        header_label = CopyableLabel(header, text=title, font=self.heading_font, 
                                    bg=self.colors['accent_light'], fg=self.colors['accent'])
        header_label.pack(anchor="w", padx=15, pady=8)
        
        return card
    
    def create_copyable_entry(self, parent, label, default, row, show=None):
        tk.Label(parent, text=label, font=self.body_font, 
                bg=self.colors['card_bg']).grid(row=row, column=0, sticky='w', padx=(0, 5), pady=3)
        
        var = tk.StringVar(value=default)
        if label == "Логин:":
            self.login_var = var
        elif label == "Пароль:":
            self.password_var = var
        elif label == "Адрес сервера:":
            self.server_var = var
        
        entry = CopyableEntry(parent, textvariable=var, font=self.body_font,
                             bg=self.colors['card_bg'], relief="solid", bd=1, show=show if show else "")
        entry.grid(row=row, column=1, sticky='ew', padx=5, pady=3)
        
        parent.grid_columnconfigure(1, weight=1)
        return var
    
    def create_button(self, parent, text, command, color, side="left", size=12, state=tk.NORMAL):
        btn = tk.Button(parent, text=text, command=command, state=state,
                       font=self.body_font, bg=color, fg="white", 
                       padx=15 if size >= 14 else 10, pady=5 if size >= 14 else 4,
                       relief="flat", cursor="hand2", bd=0,
                       activebackground=color)
        btn.pack(side=tk.LEFT if side == "left" else tk.RIGHT, padx=3)
        return btn
    
    def update_status(self, msg, is_error=False, is_loading=False):
        self.status_var.set(msg)
        if is_error:
            self.status_label.config(fg=self.colors['danger'])
        elif is_loading:
            self.status_label.config(fg=self.colors['warning'])
            self.progress.start(10)
        else:
            self.status_label.config(fg=self.colors['success'])
            self.progress.stop()
        self.root.update_idletasks()
    
    def select_file(self):
        filename = filedialog.askopenfilename(
            title="Выберите отчет в формате Excel",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        if filename:
            self.file_path_var.set(filename)
            self.update_status("📁 Файл выбран")
    
    def on_period_change(self, event):
        if self.period_var.get() == 'Произвольный':
            self.date_frame.pack(fill=tk.X, pady=3)
        else:
            self.date_frame.pack_forget()
    
    def on_employee_search(self, event):
        search_text = self.employee_var.get().strip().lower()
        
        if self.search_timer:
            self.root.after_cancel(self.search_timer)
        
        if len(search_text) == 0:
            self.employee_combo['values'] = self.all_employees[:50]
            return
        
        def do_search():
            if len(search_text) >= 1:
                matches = [emp for emp in self.all_employees 
                          if emp.lower().startswith(search_text)]
                if not matches:
                    matches = [emp for emp in self.all_employees 
                              if search_text in emp.lower()]
                self.employee_combo['values'] = matches[:50]
                if matches:
                    self.employee_combo.event_generate('<Down>')
            else:
                self.employee_combo['values'] = self.all_employees[:50]
        
        self.search_timer = self.root.after(150, do_search)
    
    def on_employee_focus(self, event):
        if not self.employee_var.get().strip():
            self.employee_combo['values'] = self.all_employees[:50]
    
    def on_employee_select(self, event):
        employee = self.employee_var.get()
        if employee and employee in self.staff_data:
            self.update_staff_info()
    
    def update_staff_info(self):
        employee = self.employee_var.get()
        if not employee or employee not in self.staff_data:
            return
        
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        
        staff_data = self.staff_data[employee]
        
        info = []
        info.append("="*50)
        info.append(f"👤 {employee}")
        info.append("="*50)
        info.append(f"ID: {staff_data.get('id', '—')}")
        info.append(f"Табельный номер: {staff_data.get('tabel_number', '—')}")
        
        status = staff_data.get('is_active', 0)
        info.append(f"Статус: {'Активен' if status == 1 else 'Неактивен'}")
        info.append("")
        
        if 'division' in staff_data and staff_data['division']:
            div = staff_data['division']
            if isinstance(div, dict) and 'name' in div:
                info.append(f"Подразделение: {div['name']}")
            else:
                info.append(f"Подразделение: {div}")
        else:
            info.append("Подразделение: —")
        
        if 'position' in staff_data and staff_data['position']:
            pos = staff_data['position']
            if isinstance(pos, dict) and 'name' in pos:
                info.append(f"Должность: {pos['name']}")
            else:
                info.append(f"Должность: {pos}")
        else:
            info.append("Должность: —")
        
        if 'hiring_date' in staff_data:
            info.append(f"Дата приема: {staff_data['hiring_date']}")
        if 'dismissed_date' in staff_data:
            info.append(f"Дата увольнения: {staff_data['dismissed_date']}")
        
        info.append("")
        info.append("-"*50)
        info.append("📇 Карты доступа:")
        
        identifiers = staff_data.get('identifier', [])
        if isinstance(identifiers, list) and identifiers:
            for ident in identifiers:
                if isinstance(ident, dict):
                    info.append(f"  • {ident.get('identifier', '—')}")
        else:
            info.append("  Нет карт доступа")
        
        self.info_text.insert(tk.END, '\n'.join(info))
        self.info_text.config(state=tk.DISABLED)
    
    def load_objects_from_data(self):
        if not self.employee_data:
            messagebox.showwarning("Предупреждение", "Сначала загрузите данные из PERCo или Excel")
            return
        
        objects = set()
        for events in self.employee_data.values():
            for event in events:
                zone_exit = str(event.get('zone_exit', '')).strip()
                zone_enter = str(event.get('zone_enter', '')).strip()
                
                if zone_exit and zone_exit not in ['Неконтролируемая территория', '']:
                    objects.add(zone_exit)
                if zone_enter and zone_enter not in ['Неконтролируемая территория', '']:
                    objects.add(zone_enter)
                
                from_place = str(event.get('from_place', '')).strip()
                to_place = str(event.get('to_place', '')).strip()
                if from_place and from_place not in ['Неконтролируемая территория', '']:
                    objects.add(from_place)
                if to_place and to_place not in ['Неконтролируемая территория', '']:
                    objects.add(to_place)
        
        self.room_objects = sorted(objects)
        self.object_combo['values'] = self.room_objects
        if self.room_objects and not self.object_var.get():
            self.object_combo.set(self.room_objects[0])
        self.update_status(f"✅ Загружено {len(self.room_objects)} объектов")
    
    # ---------- API МЕТОДЫ ----------
    def connect_api(self):
        server = self.server_var.get().strip()
        login = self.login_var.get().strip()
        password = self.password_var.get()
        
        if not all([server, login, password]):
            messagebox.showerror("Ошибка", "Заполните все поля подключения")
            return
        
        if server.endswith('/api'):
            server = server[:-4]
        
        self.update_status("🔄 Подключение к API...", is_loading=True)
        self.root.config(cursor="watch")
        
        try:
            self.api = PERCoAPI(server, login, password)
            success, message = self.api.login()
            
            if success:
                self.is_connected = True
                self.connection_status = "connected"
                self.status_indicator.config(text="● Подключено", fg=self.colors['success'])
                self.connect_btn.config(state=tk.DISABLED)
                self.disconnect_btn.config(state=tk.NORMAL)
                self.load_staff_btn.config(state=tk.NORMAL)
                self.load_events_btn.config(state=tk.NORMAL)
                self.refresh_objects_btn.config(state=tk.NORMAL)
                self.connection_info.config(text=f"Подключено к {server}")
                
                self.update_status("✅ Подключено к PERCo-Web API")
                messagebox.showinfo("Успех", "Подключение к API установлено")
                
                self.load_staff_list()
                self.load_from_api()
                
            else:
                self.update_status(f"❌ {message}", is_error=True)
                messagebox.showerror(
                    "Ошибка подключения",
                    f"Не удалось подключиться к PERCo-Web API:\n\n{message}\n\n"
                    "Проверьте:\n"
                    "1. Правильность адреса сервера\n"
                    "2. Доступность сервера в сети\n"
                    "3. Правильность логина и пароля\n"
                    "4. Используется ли HTTPS (попробуйте http://)\n"
                    "5. Включен ли модуль PERCo-WM04 'Интеграция с внешними системами'"
                )
        except Exception as e:
            self.update_status(f"❌ Ошибка: {str(e)}", is_error=True)
            messagebox.showerror("Ошибка", f"Ошибка подключения:\n{str(e)}")
        finally:
            self.root.config(cursor="")
    
    def disconnect_api(self):
        self.api = None
        self.is_connected = False
        self.connection_status = "disconnected"
        self.status_indicator.config(text="● Отключено", fg=self.colors['danger'])
        self.connect_btn.config(state=tk.NORMAL)
        self.disconnect_btn.config(state=tk.DISABLED)
        self.load_staff_btn.config(state=tk.DISABLED)
        self.load_events_btn.config(state=tk.DISABLED)
        self.refresh_objects_btn.config(state=tk.DISABLED)
        self.connection_info.config(text="")
        self.employee_combo['values'] = []
        self.all_employees = []
        self.update_status("🔌 Отключено от API")
    
    def load_staff_list(self):
        if not self.is_connected or not self.api:
            return
        
        self.update_status("🔄 Загрузка персонала из PERCo...", is_loading=True)
        self.root.config(cursor="watch")
        
        try:
            success, data = self.api.get_staff_list()
            
            if success:
                self.staff_data = {}
                employee_names = []
                
                for staff in data:
                    if isinstance(staff, dict):
                        staff_id = staff.get('id')
                        full_name = None
                        
                        if 'last_name' in staff and 'first_name' in staff:
                            parts = []
                            if staff.get('last_name'):
                                parts.append(str(staff['last_name']))
                            if staff.get('first_name'):
                                parts.append(str(staff['first_name']))
                            if staff.get('middle_name'):
                                parts.append(str(staff['middle_name']))
                            full_name = ' '.join(parts) if parts else None
                        elif 'fullName' in staff:
                            full_name = staff['fullName']
                        elif 'name' in staff:
                            full_name = staff['name']
                        
                        if staff_id and full_name:
                            self.staff_data[full_name] = staff
                            employee_names.append(full_name)
                
                self.all_employees = sorted(employee_names)
                self.employee_list = self.all_employees
                self.employee_combo['values'] = self.all_employees[:50]
                if self.all_employees and not self.employee_var.get():
                    self.employee_combo.set('')
                
                self.update_status(f"✅ Загружено {len(employee_names)} сотрудников (персонала)")
            else:
                self.update_status(f"❌ Ошибка загрузки персонала", is_error=True)
                messagebox.showwarning(
                    "Ошибка загрузки",
                    f"Не удалось загрузить список сотрудников (персонала):\n{data}"
                )
        except Exception as e:
            self.update_status(f"❌ Ошибка: {str(e)}", is_error=True)
        finally:
            self.root.config(cursor="")
    
    def get_period_dates(self):
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        period = self.period_var.get()
        
        if period == 'Сегодня':
            start_date = today
            end_date = today + timedelta(days=1) - timedelta(seconds=1)
        elif period == 'Вчера':
            start_date = today - timedelta(days=1)
            end_date = today - timedelta(seconds=1)
        elif period == 'За последние 7 дней':
            start_date = today - timedelta(days=7)
            end_date = today + timedelta(days=1) - timedelta(seconds=1)
        elif period == 'За последние 30 дней':
            start_date = today - timedelta(days=30)
            end_date = today + timedelta(days=1) - timedelta(seconds=1)
        elif period == 'Текущий месяц':
            start_date = today.replace(day=1)
            next_month = today.replace(day=28) + timedelta(days=4)
            end_date = next_month.replace(day=1) - timedelta(seconds=1)
        elif period == 'Прошлый месяц':
            first_day_current = today.replace(day=1)
            last_day_prev = first_day_current - timedelta(seconds=1)
            start_date = last_day_prev.replace(day=1)
            end_date = last_day_prev
        elif period == 'Произвольный':
            try:
                start_str = self.start_date_var.get().strip()
                end_str = self.end_date_var.get().strip()
                
                if not start_str or not end_str:
                    return None, None
                
                start_date = datetime.strptime(start_str, '%d.%m.%Y')
                end_date = datetime.strptime(end_str, '%d.%m.%Y')
                end_date = end_date.replace(hour=23, minute=59, second=59)
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ДД.ММ.ГГГГ")
                return None, None
        else:
            start_date = today.replace(day=1)
            next_month = today.replace(day=28) + timedelta(days=4)
            end_date = next_month.replace(day=1) - timedelta(seconds=1)
        
        return start_date, end_date
    
    def load_from_api(self):
        if not self.is_connected or not self.api:
            messagebox.showwarning("Предупреждение", "Сначала подключитесь к API")
            return
        
        start_date, end_date = self.get_period_dates()
        if not start_date or not end_date:
            return
        
        # Получаем ID выбранного сотрудника для фильтрации
        person_id = None
        employee_name = self.employee_var.get().strip()
        if employee_name and employee_name in self.staff_data:
            person_id = self.staff_data[employee_name].get('id')
        
        self.update_status("🔄 Загрузка событий из PERCo (Отчет о проходах)...", is_loading=True)
        self.output_text.delete(1.0, tk.END)
        self.root.config(cursor="watch")
        
        try:
            success, events = self.api.get_access_events(start_date, end_date, person_id)
            
            if success and events:
                print(f"Получено {len(events)} событий")
                
                object_name = self.object_var.get().strip() or "ЗИФ"
                processed = process_data_from_api(events, object_name)
                
                if processed:
                    self.employee_data = {}
                    for event in processed:
                        key = f"{event['person_name']}|{event.get('person_id', '')}"
                        if key not in self.employee_data:
                            self.employee_data[key] = []
                        self.employee_data[key].append(event)
                    
                    # Обновляем список сотрудников
                    employee_names = sorted(set([e['person_name'] for e in processed]))
                    self.employee_combo['values'] = employee_names[:50]
                    if employee_names and not self.employee_var.get():
                        self.employee_combo.set('')
                    
                    # Обновляем список объектов
                    self.load_objects_from_data()
                    
                    self.update_status(f"✅ Загружено {len(processed)} событий")
                    messagebox.showinfo("Успех", f"Загружено {len(processed)} событий\n"
                                                  f"Период: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}")
                else:
                    self.update_status("❌ Нет данных для обработки", is_error=True)
                    messagebox.showwarning("Нет данных", 
                        f"Нет данных для обработки за период:\n{start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}")
            else:
                self.update_status(f"❌ Ошибка загрузки или нет данных", is_error=True)
                messagebox.showwarning("Нет данных", 
                    f"Не удалось загрузить события или нет данных за период:\n{start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}")
                
        except Exception as e:
            self.update_status(f"❌ Ошибка: {str(e)}", is_error=True)
            messagebox.showerror("Ошибка", f"Ошибка при загрузке:\n{str(e)}")
        finally:
            self.root.config(cursor="")
    
    def load_from_excel(self):
        file_path = self.file_path_var.get().strip()
        if not file_path:
            messagebox.showwarning("Предупреждение", "Выберите файл Excel")
            return
        
        self.update_status("🔄 Загрузка из Excel...", is_loading=True)
        self.output_text.delete(1.0, tk.END)
        
        try:
            df = load_excel(file_path)
            if df is None:
                self.update_status("❌ Ошибка загрузки файла", is_error=True)
                messagebox.showerror("Ошибка", "Не удалось загрузить файл")
                return
            
            required_cols = ['Фамилия', 'Имя', 'Отчество', 'Дата', 'Выход из', 'Вход в']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                self.update_status("❌ Неверная структура файла", is_error=True)
                messagebox.showerror("Ошибка", f"Отсутствуют колонки: {', '.join(missing_cols)}")
                return
            
            object_name = self.object_var.get().strip() or "ЗИФ"
            processed, error = process_data_from_excel(df, object_name)
            
            if error:
                self.update_status(f"❌ {error}", is_error=True)
                messagebox.showerror("Ошибка", error)
                return
            
            if processed:
                self.employee_data = {}
                for event in processed:
                    key = f"{event['person_name']}|{event.get('person_id', '')}"
                    if key not in self.employee_data:
                        self.employee_data[key] = []
                    self.employee_data[key].append(event)
                
                employee_names = sorted(set([e['person_name'] for e in processed]))
                self.employee_combo['values'] = employee_names[:50]
                if employee_names and not self.employee_var.get():
                    self.employee_combo.set('')
                
                self.load_objects_from_data()
                
                self.update_status(f"✅ Загружено {len(processed)} записей из Excel")
                messagebox.showinfo("Успех", f"Загружено {len(processed)} записей из Excel")
            else:
                self.update_status("❌ Нет данных", is_error=True)
                messagebox.showwarning("Нет данных", "Нет данных для обработки")
                
        except Exception as e:
            self.update_status(f"❌ Ошибка: {str(e)}", is_error=True)
            messagebox.showerror("Ошибка", f"Ошибка загрузки:\n{str(e)}")
    
    # ---------- ОСНОВНОЙ РАСЧЕТ ----------
    def run_calculation(self):
        if self.processing:
            return
        
        object_name = self.object_var.get().strip()
        if not object_name:
            messagebox.showerror("Ошибка", "Выберите объект из списка (или обновите список объектов)")
            return
        
        try:
            norm = float(self.norm_var.get().replace(',', '.'))
            if norm <= 0:
                raise ValueError
        except:
            messagebox.showerror("Ошибка", "Норма должна быть положительным числом")
            return
        
        if not self.employee_data:
            messagebox.showwarning("Предупреждение", "Сначала загрузите данные из PERCo или Excel")
            return
        
        self.processing = True
        self.run_btn.config(state=tk.DISABLED)
        self.save_btn.config(state=tk.DISABLED)
        self.output_text.delete(1.0, tk.END)
        self.update_status("🔄 Выполняется расчет...", is_loading=True)
        self.root.config(cursor="watch")
        
        def target():
            try:
                all_data = []
                for key, events in self.employee_data.items():
                    all_data.extend(events)
                
                # Получаем имя выбранного сотрудника для фильтрации
                selected_employee = self.employee_var.get().strip()
                if not selected_employee:
                    selected_employee = None
                
                results = calculate_results(all_data, norm, object_name, selected_employee)
                report = generate_report(results, norm, object_name)
                self.root.after(0, self.on_calculation_finished, report, None)
                    
            except Exception as e:
                self.root.after(0, self.on_calculation_finished, None, str(e))
        
        threading.Thread(target=target, daemon=True).start()
    
    def on_calculation_finished(self, report, error):
        self.processing = False
        self.run_btn.config(state=tk.NORMAL)
        self.progress.stop()
        self.root.config(cursor="")
        
        if error:
            self.output_text.insert(tk.END, f"❌ ОШИБКА:\n{error}", ("bad",))
            self.update_status(f"❌ {error}", is_error=True)
            messagebox.showerror("Ошибка", error)
            return
        
        self.current_report = report
        self.current_report_text = '\n'.join(report)
        
        for line in report:
            self._insert_formatted_text(line)
            self.output_text.insert(tk.END, "\n")
        
        self.save_btn.config(state=tk.NORMAL)
        self.update_status("✅ Расчет завершен")
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        saved_file = save_report_to_file_auto(report, script_dir)
        if saved_file:
            self.update_status(f"💾 Отчет сохранен: {os.path.basename(saved_file)}")
            self.output_text.insert(tk.END, f"\n\n✅ Отчет автоматически сохранен в файл: {saved_file}", ("good",))
    
    def _insert_formatted_text(self, text):
        emoji_pattern = re.compile(r'[\U0001F300-\U0001F6FF\U0001F900-\U0001F9FF\U0001FA70-\U0001FAFF\U00002600-\U000027BF\U0001F100-\U0001F1FF]+')
        
        if emoji_pattern.search(text):
            parts = []
            last_end = 0
            for match in emoji_pattern.finditer(text):
                start, end = match.span()
                if start > last_end:
                    parts.append(('text', text[last_end:start]))
                parts.append(('emoji', text[start:end]))
                last_end = end
            if last_end < len(text):
                parts.append(('text', text[last_end:]))
            for typ, t in parts:
                if typ == 'emoji':
                    self.output_text.insert(tk.END, t, "emoji")
                else:
                    self._insert_text_with_tags(t)
        else:
            self._insert_text_with_tags(text)
    
    def _insert_text_with_tags(self, text):
        if "ОТЧЁТ:" in text or "Норма:" in text:
            self.output_text.insert(tk.END, text, "header")
        elif "Процент от нормы" in text:
            match = re.search(r'(\d+\.\d+)%', text)
            if match:
                percent = float(match.group(1))
                tag = "good" if percent >= 100 else ("warning" if percent >= 75 else "bad")
                parts = text.split(match.group(1)+'%')
                self.output_text.insert(tk.END, parts[0])
                self.output_text.insert(tk.END, f"{percent:.4f}%", tag)
                if len(parts) > 1:
                    self.output_text.insert(tk.END, parts[1])
            else:
                self.output_text.insert(tk.END, text)
        elif re.match(r'^\s*\d{2}\.\d{2}\.\d{4}', text):
            parts = text.split(None, 2)
            if len(parts) >= 2:
                date_part = parts[0]
                time_part = parts[1] if len(parts) > 1 else ""
                rest = " ".join(parts[2:]) if len(parts) > 2 else ""
                self.output_text.insert(tk.END, date_part, "date")
                self.output_text.insert(tk.END, f" {time_part} ", "time")
                self.output_text.insert(tk.END, rest)
            else:
                self.output_text.insert(tk.END, text)
        elif "Общее время:" in text or "Всего часов:" in text:
            self.output_text.insert(tk.END, text, "time")
        elif "Сотрудник:" in text:
            self.output_text.insert(tk.END, text, "header")
        else:
            self.output_text.insert(tk.END, text)
    
    def clear_output(self):
        self.output_text.delete(1.0, tk.END)
        self.current_report = None
        self.current_report_text = None
        self.save_btn.config(state=tk.DISABLED)
        self.update_status("🧹 Вывод очищен")
    
    def copy_to_clipboard(self):
        if self.current_report_text:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.current_report_text)
            self.update_status("📋 Отчет скопирован")
            messagebox.showinfo("Успех", "Текст отчета скопирован в буфер обмена")
        else:
            messagebox.showwarning("Нет данных", "Сначала выполните расчет")
    
    def save_report_dialog(self):
        if not self.current_report:
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            if save_report_to_path(self.current_report, file_path):
                messagebox.showinfo("Успех", f"Отчет сохранен в {file_path}")
                self.update_status("💾 Отчет сохранен")
            else:
                messagebox.showerror("Ошибка", "Не удалось сохранить файл")


def main():
    root = tk.Tk()
    app = ModernApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()