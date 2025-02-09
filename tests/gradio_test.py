import os
import gradio as gr

def chatbot_response(message, history):
    # Simulate a response from the chatbot
    bot_message = "This is a response to: " + message
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": bot_message})
    return "", history

def take_notes(note, notes):
    # Add the note to the notes
    notes.append(note)
    return "", "\n".join(notes)

def update_notes(history, notes):
    # Append chat history to notes
    chat_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
    notes.append(chat_text)
    return "\n".join(notes)

with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column():
            chatbot = gr.Chatbot(type="messages")
            msg = gr.Textbox(label="User Message")
            chat_history = gr.State([])  # Store chat history
            msg.submit(chatbot_response, [msg, chat_history], [msg, chatbot, chat_history])

        with gr.Column():
            with gr.Tab("Chat Notes"):
                notes = gr.Textbox(label="Chat Notes", lines=10, interactive=True)
                note_input = gr.Textbox(label="Take a Note")
                notes_list = gr.State([])  # Store notes
                note_input.submit(take_notes, [note_input, notes_list], [note_input, notes, notes_list])
                chat_history.change(update_notes, [chat_history, notes_list], notes)
            with gr.Tab("My Notes"):
                notes = gr.Textbox(label="My Notes", lines=10, interactive=True)
                note_input = gr.Textbox(label="Take a Note")
                notes_list = gr.State([])  # Store notes
                note_input.submit(take_notes, [note_input, notes_list], [note_input, notes, notes_list])
                chat_history.change(update_notes, [chat_history, notes_list], notes)


if __name__ == "__main__":
    favicon_path = "oxfavicon.png"
    
    # Debug: Check if file exists
    if not os.path.exists(favicon_path):
        print(f"Warning: Favicon not found at {os.path.abspath(favicon_path)}")
        
    demo.launch(
        show_error=True,
        favicon_path=favicon_path
    )