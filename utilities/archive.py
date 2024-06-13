"""

async def get_poll_post_items(
    db: AsyncSession,
    post_id: UUID
):

    result = await db.execute(select(PollQues).where(PollQues.post_id == post_id))
    poll_data = result.scalars().all()
    
    poll_dict = {}
    
    for detail in poll_data:
        qstn_key = (detail.qstn_seq_num, detail.ques_text)
        if qstn_key not in poll_dict:
            poll_dict[qstn_key] = {
                "qstn_seq_num": detail.qstn_seq_num,
                "ques_text": detail.ques_text,
                "allow_multiple": detail.allow_multiple,
                "choices": []
            }
        poll_dict[qstn_key]["choices"].append({
            "poll_item_id": str(detail.poll_item_id),
            "ans_seq_letter": detail.ans_seq_letter,
            "ans_text": detail.ans_text
        })
        
    poll_questions = [
        PollQuestionRequest(
            qstn_seq_num=k[0],
            ques_text=k[1],
            allow_multiple=v["allow_multiple"],
            choices=[PollQuesChoicesRequest(**choice) for choice in v["choices"]]
        )
        for k, v in poll_dict.items()
    ]
    
    return poll_questions
"""