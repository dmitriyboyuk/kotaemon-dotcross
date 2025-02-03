from typing import Optional

import gradio as gr
from ktem.app import BasePage
from ktem.db.models import IssueReport, engine
from sqlmodel import Session

import flowsettings

# print("\n=== Debug - Feedback Settings ===")
# print("Loading flowsettings module:", flowsettings.__file__)
# print("Environment variables loaded in flowsettings:")
# for key in dir(flowsettings):
#     if key.startswith('KH_FEEDBACK'):
#         print(f"{key} = {getattr(flowsettings, key)}")
# print("===============================\n")

class ReportIssue(BasePage):
    def __init__(self, app):
        self._app = app
        self.on_building_ui()

    def on_building_ui(self):
        with gr.Accordion(label="Feedback", open=False):
            # Get feedback labels from flowsettings
            correctness_label = getattr(flowsettings, "KH_FEEDBACK_CORRECTNESS_LABEL", "Was the response correct?")
            correct_option = getattr(flowsettings, "KH_FEEDBACK_CORRECT", "Correct")
            incorrect_option = getattr(flowsettings, "KH_FEEDBACK_INCORRECT", "Incorrect")

            sufficiency_label = getattr(flowsettings, "KH_FEEDBACK_DATA_LABEL", "Was data retrieved sufficient?")
            sufficient_option = getattr(flowsettings, "KH_FEEDBACK_DATA_SUFFICIENT", "Sufficient")
            insufficient_option = getattr(flowsettings, "KH_FEEDBACK_DATA_INSUFFICIENT", "Insufficient")

            # print("\n=== Debug - Feedback UI Values ===")
            # print(f"Correctness Question: {correctness_label}")
            # print(f"Correctness Options: {correct_option}, {incorrect_option}")
            # print(f"Data Question: {sufficiency_label}")
            # print(f"Data Options: {sufficient_option}, {insufficient_option}")
            # print("===============================\n")

            self.correctness = gr.Radio(
                choices=[
                    (correct_option, "correct"),
                    (incorrect_option, "incorrect"),
                ],
                label=correctness_label,
                value=None
            )

            # Second radio group for evidence sufficiency
            self.issues = gr.Radio(
                choices=[
                    (sufficient_option, "sufficient_data"),
                    (insufficient_option, "insufficient_data"),
                ],
                label=sufficiency_label,
                value=None
            )

            # Additional details textbox
            self.more_detail = gr.Textbox(
                placeholder=(
                    "More detail (e.g. how wrong is it, what is the "
                    "correct answer, etc...)"
                ),
                container=False,
                lines=3,
            )
            gr.Markdown(
                "This will send the current chat and the user settings to "
                "help with investigation"
            )
            self.report_btn = gr.Button("Report")

    def report(
        self,
        correctness: str,
        issues: str,
        more_detail: str,
        conv_id: str,
        chat_history: list,
        settings: dict,
        user_id: Optional[int],
        info_panel: str,
        chat_state: dict,
        *selecteds,
    ):
        selecteds_ = {}
        for index in self._app.index_manager.indices:
            if index.selector is not None:
                if isinstance(index.selector, int):
                    selecteds_[str(index.id)] = selecteds[index.selector]
                elif isinstance(index.selector, tuple):
                    selecteds_[str(index.id)] = [selecteds[_] for _ in index.selector]
                else:
                    print(f"Unknown selector type: {index.selector}")

        with Session(engine) as session:
            issue = IssueReport(
                issues={
                    "correctness": correctness,
                    "issues": [issues] if issues else [],
                    "more_detail": more_detail,
                },
                chat={
                    "conv_id": conv_id,
                    "chat_history": chat_history,
                    "info_panel": info_panel,
                    "chat_state": chat_state,
                    "selecteds": selecteds_,
                },
                settings=settings,
                user=user_id,
            )
            session.add(issue)
            session.commit()
        gr.Info("Thank you for your feedback")
