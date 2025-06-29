from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

class ConversationMemory:
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
        self.session_timeout = timedelta(hours=1)

    def get_or_create_session(self, session_id: str) -> Dict:
        if session_id not in self.sessions:
            self.create_session(session_id)
        return self.sessions[session_id]

    def create_session(self, session_id: str) -> None:
        self.sessions[session_id] = {
            'start_time': datetime.now(),
            'last_updated': datetime.now(),
            'turn_count': 0,
            'conversation_history': [],
            'collected_info': {
                'personal': {},
                'medical': {},
                'preferences': {},
                'appointments': [],
                'entities': {}
            },
            'current_context': {},
            'session_id': session_id,
            'is_first_interaction': True,
            'current_step': 0,
            # Pipeline step tracking
            'completed_greeting': False,
            'completed_symptoms': False,
            'completed_patient_history': False,
            'completed_appointment_preference': False,
            'asked_greeting': False,
            'asked_symptoms': False,
            'asked_patient_history': False,
            'asked_appointment_preference': False,
            # Appointment specific tracking
            'appointment_scheduled': False,
            'appointment_confirmed': False,
            # Pending questions
            'pending_questions': []
        }

    def update_session(self, session_id: str, user_message: str, bot_response: str,
                       entities: Optional[Dict] = None, intent: Optional[str] = None) -> None:
        try:
            if session_id not in self.sessions:
                self.create_session(session_id)

            session = self.sessions[session_id]
            current_time = datetime.now()

            # Check session timeout
            if current_time - session['last_updated'] > self.session_timeout:
                self.create_session(session_id)
                session = self.sessions[session_id]

            session['last_updated'] = current_time
            session['turn_count'] += 1

            interaction = {
                'timestamp': current_time.isoformat(),
                'user_message': user_message,
                'bot_response': bot_response,
                'entities': entities or {},
                'intent': intent
            }
            session['conversation_history'].append(interaction)

            if entities:
                if 'entities' not in session['collected_info']:
                    session['collected_info']['entities'] = {}
                session['collected_info']['entities'].update(entities)
                self._update_collected_info(session_id, entities)

            if len(self.sessions) > 1000:
                self._cleanup_old_sessions()

        except Exception as e:
            print(f"Error updating session {session_id}: {str(e)}")
            if session_id not in self.sessions:
                self.create_session(session_id)

    def _update_collected_info(self, session_id: str, entities: Dict[str, List[str]]) -> None:
        session = self.sessions[session_id]
        info = session['collected_info']

        if 'PERSON' in entities and entities['PERSON']:
            info['personal']['name'] = entities['PERSON'][0]

        if 'SYMPTOM' in entities and entities['SYMPTOM']:
            info['medical'].setdefault('symptoms', [])
            info['medical']['symptoms'].extend(entities['SYMPTOM'])
            info['medical']['symptoms'] = list(set(info['medical']['symptoms']))

        if 'PREVIOUS_VISIT' in entities and entities['PREVIOUS_VISIT']:
            info['medical']['previous_visit'] = entities['PREVIOUS_VISIT'][0].lower()

        appointment_updated = False

        if 'DEPARTMENT' in entities and entities['DEPARTMENT']:
            info['preferences']['department'] = entities['DEPARTMENT'][0]
            appointment_updated = True

        if 'DOCTOR' in entities and entities['DOCTOR']:
            info['preferences']['doctor'] = entities['DOCTOR'][0]
            appointment_updated = True

        temporal = {}
        if 'DATE' in entities and entities['DATE']:
            temporal['date'] = entities['DATE'][0]
            appointment_updated = True
        if 'TIME' in entities and entities['TIME']:
            temporal['time'] = entities['TIME'][0]
            appointment_updated = True

        if temporal:
            if not info['appointments']:
                info['appointments'].append({})
            info['appointments'][-1].update(temporal)

        if appointment_updated:
            if all(key in info['appointments'][-1] for key in ['date', 'time']):
                session['appointment_scheduled'] = True
            if info['preferences'].get('doctor') or info['preferences'].get('department'):
                session['appointment_confirmed'] = True

    def _cleanup_old_sessions(self) -> None:
        current_time = datetime.now()
        expired = [sid for sid, s in self.sessions.items()
                   if current_time - s['last_updated'] > self.session_timeout]
        for sid in expired:
            del self.sessions[sid]

    def get_session_info(self, session_id: str) -> Optional[Dict]:
        try:
            session = self.sessions.get(session_id)
            if session and datetime.now() - session['last_updated'] > self.session_timeout:
                self.create_session(session_id)
            return self.sessions.get(session_id)
        except Exception as e:
            print(f"Error getting session info for {session_id}: {str(e)}")
            return None

    def get_collected_info(self, session_id: str) -> Optional[Dict]:
        try:
            session = self.get_session_info(session_id)
            return session['collected_info'] if session else None
        except Exception as e:
            print(f"Error getting collected info for {session_id}: {str(e)}")
            return None

    def get_conversation_history(self, session_id: str, last_n: Optional[int] = None) -> List[Dict]:
        session = self.sessions.get(session_id)
        if not session:
            return []
        history = session['conversation_history']
        formatted_history = [{
            'user': h['user_message'],
            'assistant': h['bot_response']
        } for h in history if h.get('user_message') and h.get('bot_response')]
        return formatted_history[-last_n:] if last_n else formatted_history

    def add_pending_question(self, session_id: str, question: str) -> None:
        if session_id in self.sessions:
            self.sessions[session_id]['pending_questions'].append(question)

    def get_next_pending_question(self, session_id: str) -> Optional[str]:
        session = self.sessions.get(session_id)
        if session and session['pending_questions']:
            return session['pending_questions'].pop(0)
        return None

    def clear_session(self, session_id: str) -> None:
        if session_id in self.sessions:
            del self.sessions[session_id]

    def cleanup_expired_sessions(self) -> None:
        now = datetime.now()
        expired = [sid for sid, s in self.sessions.items()
                   if now - s['last_updated'] > self.session_timeout]
        for sid in expired:
            self.clear_session(sid)

    def save_session_to_file(self, session_id: str, filepath: str) -> None:
        if session_id in self.sessions:
            session = self.sessions[session_id].copy()
            session['start_time'] = session['start_time'].isoformat()
            session['last_updated'] = session['last_updated'].isoformat()
            with open(filepath, 'w') as f:
                json.dump(session, f, indent=2)

    def load_session_from_file(self, session_id: str, filepath: str) -> None:
        with open(filepath, 'r') as f:
            session = json.load(f)
            session['start_time'] = datetime.fromisoformat(session['start_time'])
            session['last_updated'] = datetime.fromisoformat(session['last_updated'])
            self.sessions[session_id] = session
