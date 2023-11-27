import "../assets/css/chat_message.css";

interface ChatMessageProps {
	messageContent: string,
	fromBot?: boolean
}

export const ChatMessage:React.FC<ChatMessageProps> = ({messageContent, fromBot = false}) => {
	return (
		<>
			<div className={fromBot ? "bot-message message" : "user-message message"}>
				<p>{messageContent}</p>
			</div>
		</>
	);
}