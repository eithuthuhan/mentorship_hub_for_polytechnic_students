import json

import customtkinter as ctk
from colors import Colors
from gui.ui_helpers import ask_confirm, require_text, show_error, show_success
from i18n import tr, normalize_language


class SettingsPage:
    """Premium settings page with multilingual foundation."""

    def __init__(self, app_or_parent, user, db):
        self.app = app_or_parent if hasattr(app_or_parent, "root") else None
        self.parent = self.app.root if self.app else app_or_parent
        self.user = user
        self.db = db
        self.language = normalize_language(self.user.get('preferred_language'))

        self.window = ctk.CTkToplevel(self.parent)
        self.window.title(tr(self.language, 'settings_title'))
        self.window.geometry("880x690")
        self.window.configure(fg_color=Colors.BG_LIGHT)
        self.window.transient(self.parent)
        self.window.lift()
        self.window.focus_force()
        self.window.attributes('-topmost', True)
        self.window.after(300, lambda: self.window.attributes('-topmost', False))
        self.window.grab_set()

        self.privacy_data = self._read_privacy_settings()
        self.center_window()
        self.setup_ui()

    def t(self, key, default=None):
        return tr(self.language, key, default)

    def center_window(self):
        self.window.update_idletasks()
        width = 880
        height = 690
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

    def setup_ui(self):
        container = ctk.CTkFrame(self.window, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=24, pady=22)

        hero = ctk.CTkFrame(container, fg_color=Colors.BG_WHITE, corner_radius=22, border_width=1, border_color=Colors.BORDER)
        hero.pack(fill="x", pady=(0, 18))
        top = ctk.CTkFrame(hero, fg_color="transparent")
        top.pack(fill="x", padx=24, pady=22)
        ctk.CTkLabel(top, text=self.t('settings_title'), font=("Arial", 28, "bold"), text_color=Colors.TEXT_DARK).pack(anchor="w")
        ctk.CTkLabel(top, text=self.t('settings_subtitle'), font=("Arial", 13), text_color=Colors.TEXT_MUTED, wraplength=760, justify="left").pack(anchor="w", pady=(8, 0))

        body = ctk.CTkFrame(container, fg_color="transparent")
        body.pack(fill="both", expand=True)

        left = ctk.CTkFrame(body, fg_color=Colors.BG_WHITE, width=240, corner_radius=22, border_width=1, border_color=Colors.BORDER)
        left.pack(side="left", fill="y", padx=(0, 16))
        left.pack_propagate(False)

        right = ctk.CTkFrame(body, fg_color=Colors.BG_WHITE, corner_radius=22, border_width=1, border_color=Colors.BORDER)
        right.pack(side="left", fill="both", expand=True)

        self._build_summary_panel(left)
        self._build_tabs(right)

        footer = ctk.CTkFrame(container, fg_color="transparent")
        footer.pack(fill="x", pady=(18, 0))
        ctk.CTkButton(footer, text=self.t('save_settings'), height=46, corner_radius=14, fg_color=Colors.ACCENT, hover_color=Colors.PRIMARY, text_color=Colors.TEXT_DARK, font=("Arial", 14, "bold"), command=self.save_settings).pack(side="right")

    def _build_summary_panel(self, parent):
        ctk.CTkLabel(parent, text="⚙️", font=("Arial", 40), text_color=Colors.PRIMARY).pack(pady=(24, 10))
        ctk.CTkLabel(parent, text=self.user.get('full_name', ''), font=("Arial", 18, "bold"), text_color=Colors.TEXT_DARK, wraplength=180).pack(padx=18)
        ctk.CTkLabel(parent, text=self.user.get('role', 'member').replace('_', ' ').title(), font=("Arial", 12), text_color=Colors.TEXT_MUTED).pack(pady=(4, 18))

        cards = [
            (self.t('language'), normalize_language(self.user.get('preferred_language'))),
            (self.t('privacy'), self.privacy_data.get('profile', 'public').title()),
            (self.t('account_security'), 'Protected'),
        ]
        for title, value in cards:
            card = ctk.CTkFrame(parent, fg_color=Colors.BG_LIGHT, corner_radius=16, border_width=1, border_color=Colors.BORDER)
            card.pack(fill="x", padx=16, pady=8)
            ctk.CTkLabel(card, text=title, font=("Arial", 11, "bold"), text_color=Colors.TEXT_MUTED).pack(anchor="w", padx=14, pady=(12, 2))
            ctk.CTkLabel(card, text=value, font=("Arial", 14, "bold"), text_color=Colors.TEXT_DARK).pack(anchor="w", padx=14, pady=(0, 12))

        hint = ctk.CTkFrame(parent, fg_color="#EEF5FF", corner_radius=16)
        hint.pack(fill="x", padx=16, pady=(18, 0))
        ctk.CTkLabel(hint, text=self.t('language_hint'), font=("Arial", 11), text_color=Colors.TEXT_MUTED, wraplength=180, justify="left").pack(padx=14, pady=14)

    def _build_tabs(self, parent):
        tabview = ctk.CTkTabview(parent, fg_color="transparent", segmented_button_fg_color=Colors.BG_LIGHT, segmented_button_selected_color=Colors.ACCENT, segmented_button_selected_hover_color=Colors.PRIMARY, segmented_button_unselected_hover_color=Colors.BORDER)
        tabview.pack(fill="both", expand=True, padx=18, pady=18)

        tabview.add(self.t('profile_preferences'))
        self.setup_profile_tab(tabview.tab(self.t('profile_preferences')))
        tabview.add(self.t('notifications'))
        self.setup_notification_tab(tabview.tab(self.t('notifications')))
        tabview.add(self.t('privacy'))
        self.setup_privacy_tab(tabview.tab(self.t('privacy')))
        tabview.add(self.t('account_security'))
        self.setup_account_tab(tabview.tab(self.t('account_security')))

    def _section_title(self, parent, text):
        ctk.CTkLabel(parent, text=text, font=("Arial", 18, "bold"), text_color=Colors.TEXT_DARK).pack(anchor="w", pady=(10, 12))

    def _field_label(self, parent, text):
        ctk.CTkLabel(parent, text=text, font=("Arial", 12, "bold"), text_color=Colors.TEXT_DARK, anchor="w").pack(fill="x", pady=(10, 6))

    def setup_profile_tab(self, parent):
        self._section_title(parent, self.t('profile_preferences'))
        self._field_label(parent, self.t('display_name'))
        self.display_name = ctk.CTkEntry(parent, height=42, corner_radius=12, border_color=Colors.BORDER)
        self.display_name.insert(0, self.user.get('full_name', ''))
        self.display_name.pack(fill="x")

        self._field_label(parent, self.t('language'))
        current_language = normalize_language(self.user.get('preferred_language'))
        self.language_var = ctk.StringVar(value=current_language)
        lang_combo = ctk.CTkComboBox(parent, width=240, height=42, values=["English", "Myanmar", "Japanese"], variable=self.language_var, corner_radius=12, border_color=Colors.BORDER, button_color=Colors.ACCENT, button_hover_color=Colors.PRIMARY)
        lang_combo.pack(anchor="w")
        ctk.CTkLabel(parent, text=self.t('language_hint'), font=("Arial", 11), text_color=Colors.TEXT_MUTED, wraplength=520, justify="left").pack(anchor="w", pady=(10, 0))

    def setup_notification_tab(self, parent):
        self._section_title(parent, self.t('notifications'))
        self.email_notif = ctk.BooleanVar(value=True)
        self.push_notif = ctk.BooleanVar(value=True)
        self.desktop_notif = ctk.BooleanVar(value=True)
        for text, var in [
            (self.t('email_notifications'), self.email_notif),
            (self.t('push_notifications'), self.push_notif),
            (self.t('desktop_notifications'), self.desktop_notif),
        ]:
            ctk.CTkCheckBox(parent, text=text, variable=var).pack(anchor="w", pady=6)
        ctk.CTkLabel(parent, text=self.t('notify_me_about'), font=("Arial", 13, "bold"), text_color=Colors.TEXT_DARK).pack(anchor="w", pady=(18, 8))
        self.notif_types = {
            'mentorship': ctk.BooleanVar(value=True),
            'events': ctk.BooleanVar(value=True),
            'messages': ctk.BooleanVar(value=True),
            'announcements': ctk.BooleanVar(value=True),
        }
        for key, label in [('mentorship', self.t('mentorship_updates')), ('events', self.t('event_reminders')), ('messages', self.t('new_messages')), ('announcements', self.t('announcement_updates'))]:
            ctk.CTkCheckBox(parent, text=label, variable=self.notif_types[key]).pack(anchor="w", pady=4)

    def setup_privacy_tab(self, parent):
        self._section_title(parent, self.t('privacy'))
        self._field_label(parent, self.t('profile_visibility'))
        self.profile_visible = ctk.StringVar(value=self.privacy_data.get('profile', 'public'))
        ctk.CTkRadioButton(parent, text=self.t('public_profile'), value="public", variable=self.profile_visible).pack(anchor="w", pady=4)
        ctk.CTkRadioButton(parent, text=self.t('private_profile'), value="private", variable=self.profile_visible).pack(anchor="w", pady=4)
        self._field_label(parent, self.t('contact_information'))
        self.email_visible = ctk.BooleanVar(value=self.privacy_data.get('email', 'private') == 'public')
        ctk.CTkCheckBox(parent, text=self.t('show_email'), variable=self.email_visible).pack(anchor="w", pady=4)
        self.phone_visible = ctk.BooleanVar(value=self.privacy_data.get('phone', 'private') == 'public')
        ctk.CTkCheckBox(parent, text=self.t('show_phone'), variable=self.phone_visible).pack(anchor="w", pady=4)

    def setup_account_tab(self, parent):
        self._section_title(parent, self.t('account_security'))
        self._field_label(parent, self.t('change_password'))
        self.current_pass = ctk.CTkEntry(parent, height=42, show="•", corner_radius=12, border_color=Colors.BORDER, placeholder_text=self.t('current_password'))
        self.current_pass.pack(fill="x", pady=(0, 10))
        self.new_pass = ctk.CTkEntry(parent, height=42, show="•", corner_radius=12, border_color=Colors.BORDER, placeholder_text=self.t('new_password'))
        self.new_pass.pack(fill="x", pady=(0, 10))
        self.confirm_pass = ctk.CTkEntry(parent, height=42, show="•", corner_radius=12, border_color=Colors.BORDER, placeholder_text=self.t('confirm_new_password'))
        self.confirm_pass.pack(fill="x", pady=(0, 12))
        ctk.CTkButton(parent, text=self.t('update_password'), height=40, corner_radius=12, fg_color=Colors.ACCENT, hover_color=Colors.PRIMARY, text_color=Colors.TEXT_DARK, command=self.change_password).pack(anchor="w")

        danger = ctk.CTkFrame(parent, fg_color="#FFF3F3", corner_radius=16, border_width=1, border_color="#F3C9C9")
        danger.pack(fill="x", pady=(24, 0))
        ctk.CTkLabel(danger, text=self.t('danger_zone'), font=("Arial", 16, "bold"), text_color=Colors.DANGER).pack(anchor="w", padx=16, pady=(14, 4))
        ctk.CTkLabel(danger, text=self.t('confirm_delete_message'), font=("Arial", 11), text_color=Colors.TEXT_MUTED, wraplength=520, justify="left").pack(anchor="w", padx=16, pady=(0, 10))
        ctk.CTkButton(danger, text=self.t('delete_account'), height=40, corner_radius=12, fg_color=Colors.DANGER, hover_color="#E17F7F", text_color=Colors.TEXT_DARK, command=self.delete_account).pack(anchor="w", padx=16, pady=(0, 16))

    def _read_privacy_settings(self):
        raw = self.user.get('privacy_settings')
        if isinstance(raw, dict):
            return raw
        if isinstance(raw, str) and raw.strip():
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                pass
        return {'profile': 'public', 'email': 'private', 'phone': 'private'}

    def change_password(self):
        current = self.current_pass.get()
        new = self.new_pass.get()
        confirm = self.confirm_pass.get()
        if not current or not new or not confirm:
            show_error('Please fill all fields')
            return
        if new != confirm:
            show_error('New passwords do not match')
            return
        if len(new) < 6:
            show_error('Password must be at least 6 characters')
            return
        if not self.db.update_user_password(self.user['user_id'], current, new):
            show_error('Current password is incorrect or the password could not be updated.')
            return
        show_success(self.t('password_updated'))
        self.current_pass.delete(0, 'end')
        self.new_pass.delete(0, 'end')
        self.confirm_pass.delete(0, 'end')

    def delete_account(self):
        password = self.current_pass.get()
        if not password:
            show_error('Enter your current password before deleting your account.')
            return
        if not ask_confirm(self.t('confirm_delete_message'), self.t('confirm_delete')):
            return
        if not self.db.soft_delete_user(self.user['user_id'], password):
            show_error('Current password is incorrect or the account could not be deactivated.')
            return
        show_success('Your account has been deactivated.')
        self.window.destroy()
        try:
            self.parent.destroy()
        except Exception:
            pass

    def save_settings(self):
        try:
            display_name = require_text(self.display_name.get(), 'Display Name')
        except ValueError as exc:
            show_error(str(exc))
            return
        payload = {
            'display_name': display_name,
            'preferred_language': self.language_var.get(),
            'profile_visibility': self.profile_visible.get(),
            'show_email': self.email_visible.get(),
            'show_phone': self.phone_visible.get(),
        }
        ok = self.db.update_user_settings(self.user['user_id'], payload)
        if not ok:
            show_error('Failed to save settings.')
            return
        self.user['full_name'] = payload['display_name']
        self.user['preferred_language'] = payload['preferred_language']
        self.user['privacy_settings'] = json.dumps({
            'profile': payload['profile_visibility'],
            'email': 'public' if payload['show_email'] else 'private',
            'phone': 'public' if payload['show_phone'] else 'private',
        })
        if self.app:
            self.app.refresh_language()
        show_success(self.t('settings_saved'))
        self.window.destroy()
