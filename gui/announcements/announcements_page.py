# gui/announcements/announcements_page.py
import customtkinter as ctk
from datetime import datetime


class AnnouncementsPage:
    """Main Announcements Page"""

    def __init__(self, parent, user, db):
        self.parent = parent
        self.root = parent.winfo_toplevel()
        self.user = user
        self.db = db

        self.all_announcements = []
        self.filtered_announcements = []
        self.priority_palette = {
            'urgent': ('#FDEAEA', '#D85C63', '#9B2C3D'),
            'high': ('#FFF3E3', '#F0B35E', '#8A5A10'),
            'medium': ('#EAF3FF', '#84B6FF', '#275EA3'),
            'low': ('#EDF4F7', '#AEBFD1', '#4D6072')
        }

        self.setup_ui()
        self.load_announcements()
    
    def setup_ui(self):
        """Setup announcements page UI"""
        self.main = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.main.pack(fill="both", expand=True, padx=24, pady=16)

        header = ctk.CTkFrame(self.main, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))

        title_block = ctk.CTkFrame(header, fg_color="transparent")
        title_block.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            title_block,
            text="📢 Announcements",
            font=("Arial", 30, "bold"),
            text_color="#1F3B5B"
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_block,
            text="Stay updated with academic notices, mentoring opportunities, campus events, and important member highlights.",
            font=("Arial", 13),
            text_color="#6F8098"
        ).pack(anchor="w", pady=(4, 0))

        action_block = ctk.CTkFrame(header, fg_color="transparent")
        action_block.pack(side="right")

        ctk.CTkButton(
            action_block,
            text="Refresh",
            width=110,
            height=40,
            fg_color="#84B6FF",
            hover_color="#6EA5F7",
            command=self.refresh_announcements,
        ).pack(side="right", padx=(10, 0))

        if self.user['role'] in ['teacher', 'senior_student']:
            ctk.CTkButton(
                action_block,
                text="+ New Announcement",
                width=180,
                height=40,
                fg_color="#7FC8A9",
                hover_color="#6AB494",
                command=self.open_create_announcement,
            ).pack(side="right")

        self.hero_card = ctk.CTkFrame(
            self.main,
            fg_color="#F6FAFF",
            corner_radius=18,
            border_width=1,
            border_color="#DCEBFF",
        )
        self.hero_card.pack(fill="x", pady=(0, 16))

        self.hero_inner = ctk.CTkFrame(self.hero_card, fg_color="transparent")
        self.hero_inner.pack(fill="x", padx=18, pady=18)
        self.hero_inner.grid_columnconfigure(0, weight=1)
        self.hero_inner.grid_columnconfigure(1, weight=0)

        left = ctk.CTkFrame(self.hero_inner, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew")

        self.hero_title = ctk.CTkLabel(
            left,
            text="Welcome to the announcement center",
            font=("Arial", 22, "bold"),
            text_color="#1F3B5B"
        )
        self.hero_title.pack(anchor="w")

        self.hero_subtitle = ctk.CTkLabel(
            left,
            text="Important updates and opportunities will appear here as they are published.",
            font=("Arial", 13),
            text_color="#6F8098",
            justify="left",
            wraplength=720,
        )
        self.hero_subtitle.pack(anchor="w", pady=(6, 0))

        self.stats_row = ctk.CTkFrame(self.hero_inner, fg_color="transparent")
        self.stats_row.grid(row=0, column=1, sticky="ne", padx=(12, 0))

        self.stat_cards = {}
        for key, label in [
            ("total", "Total"),
            ("pinned", "Pinned"),
            ("urgent", "Urgent"),
        ]:
            card = ctk.CTkFrame(
                self.stats_row,
                fg_color="white",
                corner_radius=14,
                border_width=1,
                border_color="#DCEBFF",
                width=110,
                height=98,
            )
            card.pack(side="left", padx=6)
            card.pack_propagate(False)
            value = ctk.CTkLabel(card, text="0", font=("Arial", 24, "bold"), text_color="#1F3B5B")
            value.pack(pady=(16, 4))
            ctk.CTkLabel(card, text=label, font=("Arial", 12), text_color="#6F8098", justify="center", wraplength=86).pack(padx=6, pady=(0, 10))
            self.stat_cards[key] = value

        filter_shell = ctk.CTkFrame(
            self.main,
            fg_color="white",
            corner_radius=16,
            border_width=1,
            border_color="#D7E6F7"
        )
        filter_shell.pack(fill="x", pady=(0, 16))

        filter_frame = ctk.CTkFrame(filter_shell, fg_color="transparent")
        filter_frame.pack(fill="x", padx=16, pady=14)

        self.search_entry = ctk.CTkEntry(
            filter_frame,
            width=300,
            height=38,
            placeholder_text="Search announcements by title, author, or content...",
            border_color="#D7E6F7",
            fg_color="#F9FBFE",
        )
        self.search_entry.pack(side="left", padx=(0, 12))
        self.search_entry.bind("<Return>", self.apply_filters)

        ctk.CTkLabel(filter_frame, text="Category", font=("Arial", 12, "bold"), text_color="#45617D").pack(side="left", padx=(4, 6))
        self.category_var = ctk.StringVar(value="All")
        self.category_combo = ctk.CTkComboBox(
            filter_frame,
            width=140,
            values=["All", "Academic", "Event", "Opportunity", "General", "Emergency"],
            variable=self.category_var,
            command=self.apply_filters,
        )
        self.category_combo.pack(side="left", padx=(0, 12))

        ctk.CTkLabel(filter_frame, text="Priority", font=("Arial", 12, "bold"), text_color="#45617D").pack(side="left", padx=(0, 6))
        self.priority_var = ctk.StringVar(value="All")
        self.priority_combo = ctk.CTkComboBox(
            filter_frame,
            width=120,
            values=["All", "urgent", "high", "medium", "low"],
            variable=self.priority_var,
            command=self.apply_filters,
        )
        self.priority_combo.pack(side="left", padx=(0, 12))

        ctk.CTkButton(filter_frame, text="Search", width=92, height=38, fg_color="#84B6FF", command=self.apply_filters).pack(side="left", padx=(0, 8))
        ctk.CTkButton(filter_frame, text="Reset", width=92, height=38, fg_color="#AEBFD1", command=self.reset_filters).pack(side="left")

        self.results_label = ctk.CTkLabel(self.main, text="", font=("Arial", 12), text_color="#6F8098")
        self.results_label.pack(anchor="w", pady=(0, 8))

        self.announcements_frame = ctk.CTkScrollableFrame(self.main, fg_color="transparent")
        self.announcements_frame.pack(fill="both", expand=True)

    def update_summary(self):
        total = len(self.all_announcements)
        pinned = len([a for a in self.all_announcements if a.get('pinned')])
        urgent = len([a for a in self.all_announcements if a.get('priority') == 'urgent'])
        self.stat_cards['total'].configure(text=str(total))
        self.stat_cards['pinned'].configure(text=str(pinned))
        self.stat_cards['urgent'].configure(text=str(urgent))

        first_name = (self.user.get('full_name') or 'Member').split()[0]
        if total == 0:
            title = f"Welcome, {first_name}"
            subtitle = "There are no announcements yet. Once updates are published, you will see academic notices, opportunities, and event highlights here."
        else:
            title = f"Welcome back, {first_name}"
            subtitle = (
                f"You currently have {total} announcement{'s' if total != 1 else ''} to explore. "
                f"Pinned notices and high-priority updates are highlighted first so you can quickly focus on what matters most."
            )
        self.hero_title.configure(text=title)
        self.hero_subtitle.configure(text=subtitle)

    def update_results_label(self):
        total = len(self.all_announcements)
        shown = len(self.filtered_announcements)
        self.results_label.configure(text=f"Showing {shown} of {total} announcements")

    def load_announcements(self):
        """Load announcements from database."""
        # Clear existing
        for widget in self.announcements_frame.winfo_children():
            widget.destroy()

        try:
            db_announcements = self.db.get_announcements(
                user_role=self.user.get('role'),
                user_department=self.user.get('department'),
                user_year=self.user.get('year'),
            )
            self.all_announcements = self.convert_db_announcements(db_announcements or [])
        except Exception as e:
            print(f"Error loading announcements: {e}")
            self.all_announcements = []

        self.filtered_announcements = self.all_announcements.copy()
        self.update_summary()
        self.update_results_label()
        self.display_announcements()
    
    def convert_db_announcements(self, db_announcements):
        """Convert database announcements to display format"""
        converted = []
        for ann in db_announcements:
            full_content = ann['content'] or ''
            preview = full_content if len(full_content) <= 190 else full_content[:187].rstrip() + '...'
            converted.append({
                'id': ann.get('announcement_id'),
                'title': ann['title'],
                'priority': ann.get('priority', 'medium'),
                'category': ann.get('category', 'General').title(),
                'content': preview,
                'full_content': full_content,
                'author': ann.get('announcer_name', 'Unknown'),
                'date': ann['created_at'].strftime("%Y-%m-%d") if hasattr(ann['created_at'], 'strftime') else str(ann['created_at']),
                'pinned': ann.get('is_pinned', False),
                'views': ann.get('views', 0)
            })
        return converted
    
    def display_announcements(self):
        """Display filtered announcements"""
        # Clear existing
        for widget in self.announcements_frame.winfo_children():
            widget.destroy()
        
        self.update_results_label()

        if not self.filtered_announcements:
            empty_frame = ctk.CTkFrame(self.announcements_frame, fg_color="white", corner_radius=16, border_width=1, border_color="#D7E6F7", height=120)
            empty_frame.pack(fill="x", pady=30, padx=8)
            empty_frame.pack_propagate(False)
            ctk.CTkLabel(empty_frame, text="No announcements match your current filters", font=("Arial", 16, "bold"), text_color="#1F3B5B").pack(pady=(24, 6))
            ctk.CTkLabel(empty_frame, text="Try resetting the search or choosing a different category or priority.", font=("Arial", 12), text_color="#6F8098").pack()
            return
        
        # Show pinned first
        pinned = [a for a in self.filtered_announcements if a['pinned']]
        others = [a for a in self.filtered_announcements if not a['pinned']]
        
        # Sort others by priority
        priority_order = {'urgent': 1, 'high': 2, 'medium': 3, 'low': 4}
        others.sort(key=lambda x: priority_order.get(x['priority'], 5))
        
        for ann in pinned + others:
            self.create_announcement_card(ann)
    
    def create_announcement_card(self, ann):
        """Create announcement card"""
        bg_color, accent, accent_text = self.priority_palette.get(ann['priority'], self.priority_palette['low'])

        card = ctk.CTkFrame(
            self.announcements_frame,
            fg_color="white",
            corner_radius=16,
            border_width=1,
            border_color="#D7E6F7"
        )
        card.pack(fill="x", pady=8, padx=6)

        outer = ctk.CTkFrame(card, fg_color="transparent")
        outer.pack(fill="x", padx=18, pady=16)

        top = ctk.CTkFrame(outer, fg_color="transparent")
        top.pack(fill="x", pady=(0, 10))

        badge_row = ctk.CTkFrame(top, fg_color="transparent")
        badge_row.pack(side="right")

        category_badge = ctk.CTkFrame(badge_row, fg_color="#EEF5FF", corner_radius=999)
        category_badge.pack(side="right", padx=(8, 0))
        ctk.CTkLabel(category_badge, text=ann['category'].upper(), font=("Arial", 10, "bold"), text_color="#3B6EA8").pack(padx=10, pady=4)

        priority_badge = ctk.CTkFrame(badge_row, fg_color=bg_color, corner_radius=999)
        priority_badge.pack(side="right")
        ctk.CTkLabel(priority_badge, text=ann['priority'].upper(), font=("Arial", 10, "bold"), text_color=accent_text).pack(padx=10, pady=4)

        title_text = ann['title']
        if ann.get('pinned'):
            title_text = "📌 " + title_text

        ctk.CTkLabel(
            top,
            text=title_text,
            font=("Arial", 18, "bold"),
            text_color="#1F3B5B",
            justify="left",
            wraplength=760,
        ).pack(anchor="w", fill="x")

        ctk.CTkLabel(
            outer,
            text=ann['content'],
            font=("Arial", 12),
            text_color="#5E738C",
            justify="left",
            wraplength=860,
        ).pack(anchor="w", pady=(0, 12))

        insight = self.build_context_line(ann)
        if insight:
            info = ctk.CTkFrame(outer, fg_color="#F7FAFE", corner_radius=12)
            info.pack(fill="x", pady=(0, 12))
            ctk.CTkLabel(info, text=insight, font=("Arial", 11), text_color="#5E738C", justify="left", wraplength=840).pack(anchor="w", padx=12, pady=10)

        footer = ctk.CTkFrame(outer, fg_color="transparent")
        footer.pack(fill="x")

        meta_text = f"Posted by {ann['author']} • {ann['date']}"
        if ann.get('views') is not None:
            meta_text += f" • {ann['views']} view{'s' if ann['views'] != 1 else ''}"
        ctk.CTkLabel(footer, text=meta_text, font=("Arial", 11), text_color="#95A4B8").pack(side="left")

        btn_text = "Read Full Notice"
        ctk.CTkButton(
            footer,
            text=btn_text,
            width=128,
            height=34,
            fg_color="#84B6FF",
            hover_color="#6EA5F7",
            command=lambda: self.read_announcement(ann)
        ).pack(side="right")

    def build_context_line(self, ann):
        category = ann.get('category', '').lower()
        if category == 'academic':
            return "Academic updates usually affect planning, deadlines, or study support. Reading the full notice early can help members prepare before schedules become busy."
        if category == 'event':
            return "Event notices often contain session goals, who should attend, and why the opportunity is useful for project growth, networking, or presentation readiness."
        if category == 'opportunity':
            return "Opportunity posts are worth checking carefully because they may connect members with mentoring, review support, portfolio development, or future career exposure."
        if category == 'emergency':
            return "Urgent notices should be reviewed as soon as possible so members understand any safety, scheduling, or platform-related action they may need to take."
        return "General notices help members stay aligned with the wider mentorship community, platform expectations, and upcoming activities."

    def build_read_more_sections(self, ann):
        category = ann.get('category', 'General').lower()
        sections = {
            'academic': [
                ("How members should prepare", "Review the full notice carefully, note any dates or suggested actions, and decide whether there is something you should complete this week. Academic announcements are most useful when they are read early enough to influence study planning."),
                ("Why it matters", "Clear academic updates reduce confusion and help members make better decisions about attendance, project pacing, and time management. Members who stay informed usually feel more confident and less rushed."),
            ],
            'event': [
                ("Why you may want to join", "Events are designed to turn general interest into practical progress. A single workshop, seminar, or review session can give members clearer direction, stronger motivation, and ideas they can apply immediately in their own work."),
                ("Good next step", "If the event sounds useful, check the events page, reserve your place early, and think about one or two questions you want answered. Members often gain more value when they attend with a clear purpose."),
            ],
            'opportunity': [
                ("Who should pay attention", "Members who want to grow faster, receive feedback, or prepare for internships and presentations should read opportunity announcements carefully. These notices often open doors that are easy to miss when ignored."),
                ("How to benefit most", "Prepare a short summary of your interests, current project, or learning goals before responding. That makes it easier for mentors, reviewers, or organizers to guide you in a meaningful way."),
            ],
            'emergency': [
                ("Immediate attention recommended", "This type of announcement should be taken seriously because it may affect safety, access, schedules, or platform use. Read it fully and share it responsibly with anyone who may be affected."),
                ("Practical reminder", "When urgent notices are published, avoid assumptions. Read the details, confirm what action is needed, and respond calmly and clearly."),
            ],
            'general': [
                ("Community value", "General announcements keep members connected to the broader life of the platform. They often provide useful context, reminders, and direction that support a healthier mentoring environment."),
                ("Simple next step", "Even when a notice does not require immediate action, taking a moment to understand it helps members stay informed, involved, and ready for upcoming opportunities."),
            ],
        }
        return sections.get(category, sections['general'])

    def apply_filters(self, event=None):
        """Apply search and filter criteria"""
        search_term = self.search_entry.get().lower().strip()
        category = self.category_var.get()
        priority = self.priority_var.get()
        
        self.filtered_announcements = []
        
        for ann in self.all_announcements:
            # Category filter
            if category != "All" and ann['category'].lower() != category.lower():
                continue
            
            # Priority filter
            if priority != "All" and ann['priority'] != priority:
                continue
            
            # Search filter
            if search_term:
                if (search_term in ann['title'].lower() or 
                    search_term in ann['content'].lower() or
                    search_term in ann['author'].lower()):
                    self.filtered_announcements.append(ann)
            else:
                self.filtered_announcements.append(ann)
        
        self.display_announcements()
    
    def reset_filters(self):
        """Reset all filters"""
        self.search_entry.delete(0, 'end')
        self.category_var.set("All")
        self.priority_var.set("All")
        self.filtered_announcements = self.all_announcements.copy()
        self.display_announcements()
    
    def search_announcements(self):
        """Search announcements"""
        self.apply_filters()
    
    def read_announcement(self, ann):
        """Open a rich announcement details dialog."""
        try:
            if ann.get('id'):
                self.db.increment_announcement_view(ann['id'])
                ann['views'] = (ann.get('views') or 0) + 1
        except Exception:
            pass

        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Announcement Details")
        dialog.geometry("860x680")
        dialog.configure(fg_color="#F6F9FE")
        dialog.transient(self.root)
        dialog.lift()
        dialog.attributes("-topmost", True)
        dialog.after(250, lambda: dialog.attributes("-topmost", False))
        dialog.grab_set()

        outer = ctk.CTkFrame(dialog, fg_color="#F6F9FE")
        outer.pack(fill="both", expand=True, padx=18, pady=18)

        top = ctk.CTkFrame(outer, fg_color="white", corner_radius=18, border_width=1, border_color="#D7E6F7")
        top.pack(fill="x", pady=(0, 14))

        title_row = ctk.CTkFrame(top, fg_color="transparent")
        title_row.pack(fill="x", padx=20, pady=(18, 10))

        ctk.CTkLabel(
            title_row,
            text=ann['title'],
            font=("Arial", 26, "bold"),
            text_color="#1F3B5B",
            justify="left",
            wraplength=640,
        ).pack(side="left", anchor="w")

        badge_wrap = ctk.CTkFrame(title_row, fg_color="transparent")
        badge_wrap.pack(side="right", padx=(12, 0))

        _, accent, accent_text = self.priority_palette.get(ann['priority'], self.priority_palette['low'])
        category_tag = ctk.CTkFrame(badge_wrap, fg_color="#EEF5FF", corner_radius=999)
        category_tag.pack(anchor="e", pady=(0, 6))
        ctk.CTkLabel(category_tag, text=ann['category'].upper(), font=("Arial", 10, "bold"), text_color="#3B6EA8").pack(padx=10, pady=4)

        priority_tag = ctk.CTkFrame(badge_wrap, fg_color=accent, corner_radius=999)
        priority_tag.pack(anchor="e")
        ctk.CTkLabel(priority_tag, text=ann['priority'].upper(), font=("Arial", 10, "bold"), text_color="white").pack(padx=10, pady=4)

        meta = ctk.CTkFrame(top, fg_color="transparent")
        meta.pack(fill="x", padx=20, pady=(0, 16))
        ctk.CTkLabel(
            meta,
            text=f"Posted by {ann['author']} • {ann['date']} • {ann.get('views', 0)} views",
            font=("Arial", 12),
            text_color="#6F8098",
        ).pack(side="left")

        body_card = ctk.CTkFrame(outer, fg_color="white", corner_radius=18, border_width=1, border_color="#D7E6F7")
        body_card.pack(fill="both", expand=True)

        body = ctk.CTkScrollableFrame(body_card, fg_color="white")
        body.pack(fill="both", expand=True, padx=8, pady=8)

        intro = ctk.CTkFrame(body, fg_color="#F7FAFE", corner_radius=14)
        intro.pack(fill="x", padx=12, pady=(10, 12))
        ctk.CTkLabel(intro, text="Quick overview", font=("Arial", 16, "bold"), text_color="#1F3B5B").pack(anchor="w", padx=14, pady=(12, 6))
        ctk.CTkLabel(
            intro,
            text=self.build_context_line(ann),
            font=("Arial", 12),
            text_color="#4D5F75",
            justify="left",
            wraplength=760,
        ).pack(anchor="w", padx=14, pady=(0, 12))

        ctk.CTkLabel(body, text="Full announcement", font=("Arial", 18, "bold"), text_color="#1F3B5B").pack(anchor="w", padx=12, pady=(0, 8))
        ctk.CTkLabel(
            body,
            text=ann.get('full_content', ann['content']),
            font=("Arial", 13),
            text_color="#42566F",
            justify="left",
            wraplength=760,
        ).pack(anchor="w", padx=12, pady=(0, 18))

        for heading, paragraph in self.build_read_more_sections(ann):
            section = ctk.CTkFrame(body, fg_color="#FFFFFF", corner_radius=14, border_width=1, border_color="#E8EFF8")
            section.pack(fill="x", padx=12, pady=(0, 12))
            ctk.CTkLabel(section, text=heading, font=("Arial", 15, "bold"), text_color="#1F3B5B").pack(anchor="w", padx=14, pady=(12, 6))
            ctk.CTkLabel(section, text=paragraph, font=("Arial", 12), text_color="#4D5F75", justify="left", wraplength=740).pack(anchor="w", padx=14, pady=(0, 12))

        tip_card = ctk.CTkFrame(body, fg_color="#EEF5FF", corner_radius=14)
        tip_card.pack(fill="x", padx=12, pady=(0, 12))
        ctk.CTkLabel(tip_card, text="Suggested next step", font=("Arial", 15, "bold"), text_color="#1F3B5B").pack(anchor="w", padx=14, pady=(12, 6))
        ctk.CTkLabel(
            tip_card,
            text="Take a practical action after reading this notice. That could mean registering for a relevant event, updating your profile, messaging a mentor, or simply noting an important deadline before it becomes easy to forget.",
            font=("Arial", 12),
            text_color="#4D5F75",
            justify="left",
            wraplength=740,
        ).pack(anchor="w", padx=14, pady=(0, 12))

        footer = ctk.CTkFrame(outer, fg_color="transparent")
        footer.pack(fill="x", pady=(12, 0))
        ctk.CTkButton(footer, text="Close", width=110, height=38, fg_color="#84B6FF", command=dialog.destroy).pack(side="right")

        dialog.focus_force()
        self.display_announcements()

    def open_create_announcement(self):
        """Open create announcement dialog"""
        from .create_announcement_page import CreateAnnouncementPage
        # Pass self (AnnouncementsPage) as parent
        CreateAnnouncementPage(self, self.user, self.db)
    
    def refresh_announcements(self):
        """Refresh announcements list"""
        self.load_announcements()