import streamlit as st
import json
import hmac
from src.session import Session
from src.graph.workflow import run_turn
from src.retrieval.db.queries import get_profile
from src.config import STAFF_ACCESS_CODE

if "session" not in st.session_state:
    st.session_state.session = Session()

sess = st.session_state.session

st.sidebar.title("RideWise Assist")
old_role = sess.role
role = st.sidebar.radio("Role", ["Customer", "Support Agent"], index=0 if sess.role == "Customer" else 1)

if role != old_role:
    sess.hard_reset()
    sess.role = role
    st.rerun()

if role == "Customer":
    cust_id = st.sidebar.text_input("Customer ID", value=sess.customer_id)
    if st.sidebar.button("Start"):
        if not cust_id:
            st.sidebar.error("Please enter a Customer ID")
        else:
            profile = get_profile(cust_id)
            if not profile:
                st.sidebar.error("Customer not found")
            else:
                if cust_id != sess.customer_id:
                    sess.hard_reset()
                    sess.customer_id = cust_id
                sess.authenticated = True
                st.sidebar.success(f"Welcome {profile['full_name']}")
elif role == "Support Agent":
    agent_name = st.sidebar.text_input("Agent name", value=sess.agent_name or "")
    staff_code = st.sidebar.text_input("Staff access code", type="password")
    if st.sidebar.button("Start"):
        if not STAFF_ACCESS_CODE or not hmac.compare_digest(staff_code, STAFF_ACCESS_CODE):
            st.sidebar.error("Invalid staff code")
        else:
            sess.hard_reset()
            sess.role = "Support Agent"
            sess.authenticated = True
            sess.agent_name = agent_name
            sess.customer_id = ""
            st.sidebar.success(f"Welcome Agent {agent_name}")

if st.sidebar.button("New conversation"):
    sess.reset()
    st.rerun()

if st.sidebar.button("Log out"):
    sess.hard_reset()
    st.rerun()

for msg in sess.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "evidence" in msg and msg["evidence"]:
            with st.expander("Evidence"):
                st.json(msg["evidence"])

user_input = st.chat_input("Type your message...", disabled=not sess.authenticated)
if user_input and sess.authenticated:
    sess.history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
        
    state_in = {
        "role": sess.role,
        "customer_id": sess.customer_id,
        "user_message": user_input,
        "history": [{"role": m["role"], "content": m["content"]} for m in sess.history[:-1]],
        "entities": {"active_booking_id": sess.active_booking_id},
        "evidence": [],
        "authenticated": sess.authenticated,
        "agent_name": sess.agent_name
    }
    
    with st.spinner("Processing..."):
        state_out = run_turn(state_in)
        
    blocked = state_out.get("blocked_reason")
    if blocked:
        ans = f"Blocked: {blocked}"
        ev = []
    else:
        ans = state_out.get("answer", "")
        ev = state_out.get("evidence", [])
        
    out_entities = state_out.get("entities", {})
    if "booking_id" in out_entities and out_entities["booking_id"]:
        sess.active_booking_id = out_entities["booking_id"]
        
    sess.history.append({"role": "assistant", "content": ans, "evidence": ev})
    
    with st.chat_message("assistant"):
        st.markdown(ans)
        if ev:
            with st.expander("Evidence"):
                st.json(ev)
