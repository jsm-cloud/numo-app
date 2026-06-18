import streamlit as st
import requests

# 1. Konfigurera den rena agent-skärmen
st.set_page_config(page_title="Numo Gemini", page_icon="🐾", layout="centered")

# Lägg till din egna PNG-hundbild från er jobb-SharePoint högst upp
st.image("https://sharepoint.com", width=250)

st.title("🐾 Numo Gemini v6.5")
st.subheader("Agent Copilot - Nummerupplysning")

# 2. Hantera minnet och sök-räknaren
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hej, jag heter Numo, välkommen hur kan jag hjälpa dig?"}]
if "search_count" not in st.session_state:
    st.session_state.search_count = 0

# 3. Visa chatten på skärmen
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 4. När agenten skriver ett sökord eller kommando i rutan
prompt = st.chat_input("Skriv sökord eller .kommando...")

if prompt:
    # Visa vad agenten skrev
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 🛠️ HANTERA SYSTEMKOMMANDON (Börjar med punkt)
    if prompt.startswith("."):
        cmd = prompt.lower().strip()
        if cmd == ".kommandon":
            answer = "### 🛠️ Tillgängliga kommandon:\n* `.kommandon` - Visar denna lista.\n* `.status` - Visar hur många sökningar som gjorts.\n* `.nollställ` - Nollställer sök-räknaren."
        elif cmd == ".status":
            answer = f"### 📊 Aktuell status:\n* Sökningar gjorda i detta pass: **{st.session_state.search_count}**"
        elif cmd == ".nollställ":
            st.session_state.search_count = 0
            answer = "🔄 Sök-räknaren har återställts till 0."
        else:
            answer = f"❌ Okänt kommando: `{prompt}`"

    # 📞 VANLIG SÖKNING MOT DIN SUPABASE-DATABAS
    else:
        st.session_state.search_count += 1
        with st.spinner("Numo söker..."):
            url = "https://supabase.co"
            headers = {
                "apikey": "sb_publishable_lPfULIddx3L4CsC8h_pf9Q_doJlSLKR",
                "Authorization": "Bearer sb_publishable_lPfULIddx3L4CsC8h_pf9Q_doJlSLKR",
                "Content-Type": "application/json"
            }
            params = {
                "namn": f"ilike.*{prompt}*"
            }
            
            try:
                response = requests.get(url, headers=headers, params=params)
                data = response.json()
                
                if data:
                    answer = f"### Sökresultat (Sökning {st.session_state.search_count}):\n\n"
                    for row in data:
                        answer += f"*   **Källstatus**: Intern träff ID {row.get('id', 'N/A')}\n"
                        answer += f"    *   **Sökresultat**: {row.get('namn', 'N/A')}\n"
                        raw_num = row.get('nummer', 'N/A')
                        formatted_num = " - ".join([raw_num[i:i+2] for i in range(0, len(raw_num), 2)]) if len(raw_num) > 4 else raw_num
                        answer += f"    *   **Telefonnummer**: **{formatted_num}**\n\n"
                else:
                    answer = f"Numret saknas i din lista. (Sökning {st.session_state.search_count})."
            except:
                answer = "Ett tekniskt fel uppstod vid databassökningen."

    # 5. Visa Numos svar för agenten
    with st.chat_message("assistant"):
        st.write(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()