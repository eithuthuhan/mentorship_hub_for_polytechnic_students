import customtkinter as ctk
from datetime import datetime

from colors import Colors
from gui.ui_helpers import show_error


class MessagesPage:
    """Premium live mentorship messages page backed by the database."""

    AUTO_REFRESH_MS = 3000

    def __init__(self, parent, user, db):
        self.parent = parent
        self.user = user
        self.db = db
        self.current_conversation = None
        self.conversations = []
        self.refresh_job = None
        self.last_loaded_request_id = None

        self.setup_ui()
        self.load_conversations()
        self.schedule_refresh()

    def setup_ui(self):
        self.main = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.main.pack(fill="both", expand=True)

        self._build_header()
        self._build_summary_row()

        body = ctk.CTkFrame(self.main, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=16, pady=(0, 10))
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=2)
        body.grid_rowconfigure(0, weight=1)

        self._build_conversation_panel(body)
        self._build_chat_panel(body)

    def _build_header(self):
        hero = ctk.CTkFrame(self.main, fg_color=Colors.BG_WHITE, corner_radius=20, border_width=1, border_color=Colors.BORDER)
        hero.pack(fill="x", padx=16, pady=(8, 12))
        hero.grid_columnconfigure(0, weight=1)
        hero.grid_columnconfigure(1, weight=0)

        left = ctk.CTkFrame(hero, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=18, pady=16)
        ctk.CTkLabel(left, text="💬 Live Messages", font=("Arial", 24, "bold"), text_color=Colors.TEXT_DARK).pack(anchor="w")
        ctk.CTkLabel(
            left,
            text="Stay connected with mentors and mentees. This inbox refreshes from the database automatically and keeps unread counts up to date.",
            font=("Arial", 12),
            text_color=Colors.TEXT_MUTED,
            wraplength=780,
            justify="left",
        ).pack(anchor="w", pady=(6, 0))

        right = ctk.CTkFrame(hero, fg_color=Colors.BG_SOFT_BLUE, corner_radius=18, border_width=1, border_color=Colors.BORDER)
        right.grid(row=0, column=1, sticky="e", padx=18, pady=16)
        ctk.CTkLabel(right, text="Sync Status", font=("Arial", 11, "bold"), text_color=Colors.TEXT_MUTED).pack(padx=18, pady=(10, 2))
        self.status_label = ctk.CTkLabel(right, text="Starting live sync", font=("Arial", 14, "bold"), text_color=Colors.PRIMARY)
        self.status_label.pack(padx=18, pady=(0, 10))

    def _build_summary_row(self):
        row = ctk.CTkFrame(self.main, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=(0, 12))
        for i in range(4):
            row.grid_columnconfigure(i, weight=1)

        self.summary_cards = {
            'threads': self._summary_card(row, 0, 'Conversations', '0', 'All mentorship threads available'),
            'unread': self._summary_card(row, 1, 'Unread', '0', 'Messages waiting for your reply'),
            'active': self._summary_card(row, 2, 'Active Chats', '0', 'Accepted or completed mentorships'),
            'selected': self._summary_card(row, 3, 'Selected', 'None', 'Current open conversation'),
        }

    def _summary_card(self, parent, column, label, value, caption):
        card = ctk.CTkFrame(parent, fg_color=Colors.BG_WHITE, corner_radius=18, border_width=1, border_color=Colors.BORDER)
        card.grid(row=0, column=column, padx=(0 if column == 0 else 6, 0), sticky='nsew')
        ctk.CTkLabel(card, text=label, font=("Arial", 12, "bold"), text_color=Colors.TEXT_MUTED).pack(anchor='w', padx=16, pady=(12, 4))
        value_label = ctk.CTkLabel(card, text=value, font=("Arial", 24, "bold"), text_color=Colors.TEXT_DARK)
        value_label.pack(anchor='w', padx=16)
        ctk.CTkLabel(card, text=caption, font=("Arial", 11), text_color=Colors.TEXT_SOFT, wraplength=180, justify='left').pack(anchor='w', padx=16, pady=(2, 12))
        return value_label

    def _build_conversation_panel(self, parent):
        panel = ctk.CTkFrame(parent, fg_color=Colors.BG_WHITE, corner_radius=20, border_width=1, border_color=Colors.BORDER)
        panel.grid(row=0, column=0, sticky='nsew', padx=(0, 8), pady=0)

        search_wrap = ctk.CTkFrame(panel, fg_color='transparent')
        search_wrap.pack(fill='x', padx=14, pady=14)
        ctk.CTkLabel(search_wrap, text='Conversation list', font=("Arial", 15, "bold"), text_color=Colors.TEXT_DARK).pack(anchor='w')
        ctk.CTkLabel(search_wrap, text='Search by person, subject, or the latest message.', font=("Arial", 11), text_color=Colors.TEXT_MUTED).pack(anchor='w', pady=(2, 8))

        entry_row = ctk.CTkFrame(search_wrap, fg_color='transparent')
        entry_row.pack(fill='x')
        self.search_entry = ctk.CTkEntry(entry_row, height=38, placeholder_text='Search conversations...')
        self.search_entry.pack(side='left', fill='x', expand=True, padx=(0, 8))
        self.search_entry.bind('<Return>', lambda _event: self.load_conversations())
        ctk.CTkButton(entry_row, text='Search', width=86, height=38, fg_color=Colors.SECONDARY, hover_color=Colors.PRIMARY, command=self.load_conversations).pack(side='left', padx=(0, 8))
        ctk.CTkButton(entry_row, text='Refresh', width=86, height=38, fg_color=Colors.SUCCESS, command=self.refresh_now).pack(side='left')

        self.conversation_count_label = ctk.CTkLabel(panel, text='0 conversations', font=("Arial", 11), text_color=Colors.TEXT_MUTED)
        self.conversation_count_label.pack(anchor='w', padx=14)

        self.conversations_frame = ctk.CTkScrollableFrame(
            panel,
            fg_color='transparent',
            scrollbar_button_color=Colors.SECONDARY,
            scrollbar_button_hover_color=Colors.PRIMARY,
        )
        self.conversations_frame.pack(fill='both', expand=True, padx=10, pady=(10, 10))

    def _build_chat_panel(self, parent):
        panel = ctk.CTkFrame(parent, fg_color=Colors.BG_WHITE, corner_radius=20, border_width=1, border_color=Colors.BORDER)
        panel.grid(row=0, column=1, sticky='nsew', padx=(8, 0), pady=0)

        header = ctk.CTkFrame(panel, fg_color='transparent')
        header.pack(fill='x', padx=16, pady=(14, 10))
        self.header_label = ctk.CTkLabel(header, text='Select a conversation', font=("Arial", 18, "bold"), text_color=Colors.TEXT_DARK)
        self.header_label.pack(anchor='w')
        self.header_subtitle = ctk.CTkLabel(header, text='Messages refresh automatically from the database.', font=("Arial", 11), text_color=Colors.TEXT_MUTED, wraplength=620, justify='left')
        self.header_subtitle.pack(anchor='w', pady=(4, 0))

        self.message_list = ctk.CTkScrollableFrame(
            panel,
            fg_color=Colors.BG_SOFTER,
            corner_radius=18,
            border_width=1,
            border_color=Colors.BORDER,
            scrollbar_button_color=Colors.SECONDARY,
            scrollbar_button_hover_color=Colors.PRIMARY,
        )
        self.message_list.pack(fill='both', expand=True, padx=16, pady=(0, 12))

        input_wrap = ctk.CTkFrame(panel, fg_color='transparent')
        input_wrap.pack(fill='x', padx=16, pady=(0, 14))
        self.message_entry = ctk.CTkEntry(input_wrap, height=42, placeholder_text='Type a message...')
        self.message_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        self.message_entry.bind('<Return>', lambda _event: self.send_message())
        self.message_entry.configure(state='disabled')
        self.send_btn = ctk.CTkButton(input_wrap, text='Send', width=90, height=42, fg_color=Colors.SUCCESS, state='disabled', command=self.send_message)
        self.send_btn.pack(side='left')

    def refresh(self):
        self.load_conversations()

    def refresh_now(self):
        self.status_label.configure(text='Refreshing now')
        self.load_conversations()

    def schedule_refresh(self):
        root = self.parent.winfo_toplevel()
        if not root.winfo_exists():
            return
        self.refresh_job = root.after(self.AUTO_REFRESH_MS, self._auto_refresh)

    def _auto_refresh(self):
        try:
            self.load_conversations(silent=True)
        finally:
            root = self.parent.winfo_toplevel()
            if root.winfo_exists():
                self.schedule_refresh()

    # def schedule_refresh(self):
    #     # 1. လက်ရှိ widget ကိုယ်တိုင် ရှိသေးရဲ့လား အရင်စစ်မယ်
    #     if not self.winfo_exists():
    #         return
            
    #     try:
    #         root = self.parent.winfo_toplevel()
    #         if root and root.winfo_exists():
    #             self.refresh_job = root.after(self.AUTO_REFRESH_MS, self._auto_refresh)
    #     except Exception:
    #         # တစ်ခုခုလွဲချော်ခဲ့ရင် refresh loop ကို ရပ်ပစ်မယ်
    #         return

    # def _auto_refresh(self):
    #     # 1. လက်ရှိ widget ဖျက်ဆီးခံလိုက်ရပြီဆိုရင် ဘာမှဆက်မလုပ်ဘဲ ရပ်မယ်
    #     if not self.winfo_exists():
    #         return

    #     try:
    #         self.load_conversations(silent=True)
    #     except Exception as e:
    #         print(f"Error loading conversations in background: {e}")
    #     finally:
    #         # 2. သေချာအောင် widget ရှိသေးလား ထပ်စစ်ပြီးမှ နောက်တစ်ကြိမ် loop ပတ်ဖို့ schedule ဆွဲမယ်
    #         if self.winfo_exists():
    #             try:
    #                 root = self.parent.winfo_toplevel()
    #                 if root and root.winfo_exists():
    #                     self.schedule_refresh()
    #             except Exception:
    #                 pass

    def _update_summary(self):
        total = len(self.conversations)
        unread = sum(int(conv.get('unread', 0) or 0) for conv in self.conversations)
        active = sum(1 for conv in self.conversations if str(conv.get('status', '')).lower() in ('accepted', 'completed'))
        selected = self.current_conversation.get('name') if self.current_conversation else 'None'
        self.summary_cards['threads'].configure(text=str(total))
        self.summary_cards['unread'].configure(text=str(unread))
        self.summary_cards['active'].configure(text=str(active))
        self.summary_cards['selected'].configure(text=selected if len(selected) <= 14 else selected[:11] + '...')
        self.conversation_count_label.configure(text=f"{total} conversation{'s' if total != 1 else ''}")

    def load_conversations(self, silent=False):
        selected_id = self.current_conversation.get('request_id') if self.current_conversation else None
        draft_text = self.message_entry.get().strip() if self.current_conversation else ''
        try:
            keyword = self.search_entry.get().strip() if hasattr(self, 'search_entry') else None
            rows = self.db.get_conversation_list(self.user['user_id'], keyword) if hasattr(self.db, 'get_conversation_list') else []
            self.conversations = []
            for row in rows:
                self.conversations.append({
                    'request_id': row.get('request_id'),
                    'other_user_id': row.get('other_user_id'),
                    'name': row.get('other_name', 'Unknown'),
                    'subject': row.get('subject', 'Mentorship'),
                    'status': row.get('status', 'pending'),
                    'last_msg': row.get('last_message') or 'No messages yet',
                    'time': self.format_display_time(row.get('last_message_time') or row.get('created_at')),
                    'unread': int(row.get('unread_count', 0) or 0),
                    'created_at': row.get('created_at'),
                })
            self.status_label.configure(text='Live sync active')
        except Exception as error:
            print(f"Error loading conversations: {error}")
            self.conversations = []
            if not silent:
                self.status_label.configure(text='Refresh failed')

        self.render_conversations()
        self._update_summary()
        if selected_id:
            match = next((conv for conv in self.conversations if conv.get('request_id') == selected_id), None)
            if match:
                self.select_conversation(match, preserve_input=True, draft_text=draft_text)
            else:
                self.current_conversation = None
                self.reset_chat_panel()
        elif not self.current_conversation:
            self.reset_chat_panel()

    def render_conversations(self):
        for widget in self.conversations_frame.winfo_children():
            widget.destroy()

        if not self.conversations:
            card = ctk.CTkFrame(self.conversations_frame, fg_color=Colors.BG_SOFT_BLUE, corner_radius=18, border_width=1, border_color=Colors.BORDER, height=180)
            card.pack(fill='x', pady=8)
            card.pack_propagate(False)
            inner = ctk.CTkFrame(card, fg_color='transparent')
            inner.pack(expand=True)
            ctk.CTkLabel(inner, text='No conversations found', font=("Arial", 18, "bold"), text_color=Colors.TEXT_DARK).pack(pady=(0, 8))
            ctk.CTkLabel(inner, text='Accepted mentorships and completed mentorship histories will appear here with real unread counts and the latest database messages.', font=("Arial", 11), text_color=Colors.TEXT_MUTED, wraplength=300, justify='center').pack()
            return

        selected_id = self.current_conversation.get('request_id') if self.current_conversation else None
        for conv in self.conversations:
            self.create_conversation_item(conv, is_selected=conv.get('request_id') == selected_id)

    def create_conversation_item(self, conv, is_selected=False):
        fg = Colors.BG_SOFT_BLUE if is_selected else Colors.BG_WHITE
        border = Colors.SECONDARY if is_selected else Colors.BORDER
        item = ctk.CTkFrame(self.conversations_frame, fg_color=fg, corner_radius=18, border_width=1, border_color=border)
        item.pack(fill='x', pady=6)
        item.grid_columnconfigure(0, weight=0)
        item.grid_columnconfigure(1, weight=1)
        item.grid_columnconfigure(2, weight=0)

        avatar = ctk.CTkLabel(item, text='👤', font=("Arial", 18), fg_color=Colors.SECONDARY, text_color=Colors.BG_WHITE, width=42, height=42, corner_radius=21)
        avatar.grid(row=0, column=0, rowspan=2, padx=(12, 12), pady=12)

        title_frame = ctk.CTkFrame(item, fg_color='transparent')
        title_frame.grid(row=0, column=1, sticky='ew', pady=(12, 0))
        ctk.CTkLabel(title_frame, text=conv['name'], font=("Arial", 13, "bold"), text_color=Colors.TEXT_DARK).pack(side='left')
        self._mini_badge(title_frame, str(conv.get('status', 'pending')).title())

        preview = conv['last_msg'][:72] + '...' if len(conv['last_msg']) > 72 else conv['last_msg']
        ctk.CTkLabel(item, text=preview, font=("Arial", 11), text_color=Colors.TEXT_MUTED, wraplength=280, justify='left').grid(row=1, column=1, sticky='w', pady=(2, 12))

        right = ctk.CTkFrame(item, fg_color='transparent')
        right.grid(row=0, column=2, rowspan=2, padx=(8, 12), pady=12)
        ctk.CTkLabel(right, text=conv['time'], font=("Arial", 10), text_color=Colors.TEXT_SOFT).pack(anchor='e')
        if conv['unread'] > 0:
            ctk.CTkLabel(right, text=str(conv['unread']), fg_color=Colors.DANGER, text_color=Colors.BG_WHITE, width=22, height=22, corner_radius=11, font=("Arial", 10, "bold")).pack(anchor='e', pady=(6, 0))

        self.bind_click_recursive(item, lambda _event, c=conv: self.select_conversation(c))

    def _mini_badge(self, parent, text):
        ctk.CTkLabel(parent, text=text, font=("Arial", 10, "bold"), fg_color=Colors.ACCENT, text_color=Colors.PRIMARY, corner_radius=999).pack(side='left', padx=(8, 0), ipadx=8, ipady=2)

    def bind_click_recursive(self, widget, callback):
        widget.bind('<Button-1>', callback)
        for child in widget.winfo_children():
            child.bind('<Button-1>', callback)
            for grandchild in child.winfo_children():
                grandchild.bind('<Button-1>', callback)

    def reset_chat_panel(self):
        self.current_conversation = None
        self.header_label.configure(text='Select a conversation')
        self.header_subtitle.configure(text='Messages refresh automatically from the database.')
        self.message_entry.configure(state='disabled')
        self.send_btn.configure(state='disabled')
        self.message_entry.delete(0, 'end')
        self._clear_message_bubbles()
        self._empty_message_state(
            'Choose a conversation to start',
            'Once you select a mentorship thread, live messages, unread tracking, and reply actions will appear here.'
        )
        self._update_summary()
        self.render_conversations()

    def select_conversation(self, conv, preserve_input=False, draft_text=''):
        self.current_conversation = conv
        self.render_conversations()
        self._update_summary()
        self.header_label.configure(text=f"{conv['name']} • {conv['subject']}")

        can_chat = str(conv.get('status', '')).lower() in ('accepted', 'completed')
        if can_chat:
            self.header_subtitle.configure(text='This thread is live. Messages are synced with the database and refresh automatically.')
            self.message_entry.configure(state='normal')
            self.send_btn.configure(state='normal')
            if preserve_input and draft_text:
                self.message_entry.delete(0, 'end')
                self.message_entry.insert(0, draft_text)
            elif not preserve_input:
                self.message_entry.delete(0, 'end')
        else:
            self.header_subtitle.configure(text=f"Chat becomes available after acceptance. Current status: {str(conv.get('status', 'pending')).title()}.")
            self.message_entry.configure(state='disabled')
            self.send_btn.configure(state='disabled')
            self.message_entry.delete(0, 'end')
        self.load_messages(conv)

    def _clear_message_bubbles(self):
        for widget in self.message_list.winfo_children():
            widget.destroy()

    def _empty_message_state(self, title, body):
        card = ctk.CTkFrame(self.message_list, fg_color=Colors.BG_WHITE, corner_radius=18, border_width=1, border_color=Colors.BORDER, height=220)
        card.pack(fill='x', pady=14)
        card.pack_propagate(False)
        inner = ctk.CTkFrame(card, fg_color='transparent')
        inner.pack(expand=True)
        ctk.CTkLabel(inner, text=title, font=("Arial", 18, "bold"), text_color=Colors.TEXT_DARK).pack(pady=(0, 8))
        ctk.CTkLabel(inner, text=body, font=("Arial", 11), text_color=Colors.TEXT_MUTED, wraplength=560, justify='center').pack()

    def load_messages(self, conv):
        self._clear_message_bubbles()
        try:
            messages = self.db.get_messages(conv['request_id']) or []
            self.db.mark_messages_as_read(conv['request_id'], self.user['user_id'])
            self.last_loaded_request_id = conv['request_id']
        except Exception as error:
            print(f"Error loading messages: {error}")
            messages = []

        status = str(conv.get('status', 'pending')).lower()
        if status not in ('accepted', 'completed'):
            self._empty_message_state(
                'Chat is locked for now',
                f"This mentorship request is currently {status}. Once it is accepted, both members will be able to exchange real-time messages here."
            )
            return
        if not messages:
            self._empty_message_state(
                'No messages yet',
                'This conversation is active. Send the first message to start the discussion, share your goals, or arrange your next mentoring session.'
            )
            return

        for msg in messages:
            self._message_bubble(msg, conv)
        try:
            self.message_list._parent_canvas.yview_moveto(1.0)
        except Exception:
            pass

    def _message_bubble(self, msg, conv):
        is_me = msg.get('sender_id') == self.user['user_id']
        outer = ctk.CTkFrame(self.message_list, fg_color='transparent')
        outer.pack(fill='x', padx=8, pady=6, anchor='e' if is_me else 'w')

        bubble = ctk.CTkFrame(
            outer,
            fg_color=Colors.SECONDARY if is_me else Colors.BG_WHITE,
            corner_radius=18,
            border_width=0 if is_me else 1,
            border_color=Colors.BORDER,
        )
        bubble.pack(anchor='e' if is_me else 'w', padx=(140, 0) if is_me else (0, 140))

        sender_name = 'You' if is_me else msg.get('sender_name', conv.get('name', 'Member'))
        time_text = self.format_display_time(msg.get('sent_at'))
        header_color = Colors.BG_WHITE if is_me else Colors.TEXT_DARK
        body_color = Colors.BG_WHITE if is_me else Colors.TEXT_DARK
        meta_text = f"{sender_name} • {time_text}"

        ctk.CTkLabel(bubble, text=meta_text, font=("Arial", 10, "bold"), text_color=header_color).pack(anchor='w', padx=14, pady=(10, 4))
        ctk.CTkLabel(
            bubble,
            text=msg.get('message', ''),
            font=("Arial", 12),
            text_color=body_color,
            wraplength=420,
            justify='left',
        ).pack(anchor='w', padx=14, pady=(0, 12))

    def send_message(self):
        msg = self.message_entry.get().strip()
        if not msg or not self.current_conversation:
            return
        try:
            result = self.db.send_message(self.current_conversation['request_id'], self.user['user_id'], msg)
        except Exception as error:
            print(f"Error sending message: {error}")
            result = -1
        if result == -1:
            show_error('Unable to send message.', 'Message')
            return
        self.message_entry.delete(0, 'end')
        self.load_messages(self.current_conversation)
        self.status_label.configure(text='Message sent')

    def format_display_time(self, value):
        if value is None:
            return '—'
        if hasattr(value, 'strftime'):
            return value.strftime('%I:%M %p').lstrip('0')
        if isinstance(value, str):
            for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S'):
                try:
                    parsed = datetime.strptime(value, fmt)
                    return parsed.strftime('%I:%M %p').lstrip('0')
                except ValueError:
                    continue
        return str(value)
