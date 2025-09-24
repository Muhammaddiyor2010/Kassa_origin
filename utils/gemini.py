from google import genai
from google.genai import types
from loader import db
# AIzaSyAv5lanqXW9KjLFtUhlrGdPvgfdcBz-s4Y

class Geminiutils():

    def __init__(self) -> None:
        self.client=  genai.Client(api_key="AIzaSyAv5lanqXW9KjLFtUhlrGdPvgfdcBz-s4Y")

   

    def add_chiqim_f(self, summa: int, kategoriya: str, izoh: str, user_id: int = 23) -> dict[str, int | str]:
        """
        Add expense to database using the provided parameters
        
        Args:
            summa: Amount of the expense
            kategoriya: Category of the expense
            izoh: Description/comment for the expense
            user_id: User ID (defaults to 23 for testing)
            
        Returns:
            Result of the database operation
        """
        try:
            # Use the actual parameters passed to the function
            add = db.add_chiqim(str(summa), kategoriya, izoh, user_id)
            print(f"Expense added: {summa} so'm for {kategoriya} - {izoh}")
            return add
        except Exception as e:
            print(f"Error adding expense: {e}")
            return {"error": str(e)}

    def add_kirim_f(self, summa: int, kategoriya: str, izoh: str, user_id: int = 23) -> dict[str, int | str]:
        """
        Add income to database using the provided parameters
        
        Args:
            summa: Amount of the income
            kategoriya: Category of the income
            izoh: Description/comment for the income
            user_id: User ID (defaults to 23 for testing)
            
        Returns:
            Result of the database operation
        """
        try:
            # Use the actual parameters passed to the function
            add = db.add_kirim(str(summa), kategoriya, izoh, user_id)
            print(f"Income added: {summa} so'm for {kategoriya} - {izoh}")
            return add
        except Exception as e:
            print(f"Error adding income: {e}")
            return {"error": str(e)}


    def get_text(self, audio_path):
        """
        Convert audio file to text using Gemini AI
        
        Args:
            audio_path (str): Path to the audio file
            
        Returns:
            str: Transcribed text
        """
        try:
            # Check if file exists
            import os
            if not os.path.exists(audio_path):
                print(f"Audio file not found: {audio_path}")
                return "Xato: Audio fayl topilmadi"
            
            # Check file size (Gemini has limits)
            file_size = os.path.getsize(audio_path)
            if file_size > 20 * 1024 * 1024:  # 20MB limit
                print(f"Audio file too large: {file_size} bytes")
                return "Xato: Audio fayl juda katta (20MB dan kichik bo'lishi kerak)"
            
            # Upload the audio file to Gemini
            myfile = self.client.files.upload(path=audio_path)
            prompt = "Ushbu o'zbek tilidagi audioni matnga aylantir"

            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[types.Content(
                    role="user", 
                    parts=[types.Part(text=prompt), types.Part(file_data=types.FileData(file_uri=myfile.uri))]
                )]
            )

            if response and response.text:
                return response.text.strip()
            else:
                print("Empty response from Gemini")
                return "Xato: AI javob bermadi"
                
        except Exception as e:
            print(f"Error in get_text: {e}")
            error_str = str(e)
            
            # Check for specific error types
            if "FAILED_PRECONDITION" in error_str and "location is not supported" in error_str:
                return "❌ Xato: Google AI xizmati sizning mintaqangizda ishlamaydi. Iltimos VPN ishlatib qayta urinib ko'ring yoki matnli xabar yuboring."
            elif "400" in error_str:
                return "❌ Xato: API so'rovida xatolik. Iltimos qayta urinib ko'ring."
            elif "403" in error_str:
                return "❌ Xato: API kaliti noto'g'ri yoki cheklangan. Administrator bilan bog'laning."
            elif "429" in error_str:
                return "❌ Xato: API limiti tugagan. Iltimos biroz kutib qayta urinib ko'ring."
            else:
                return "❌ Xato: Audio faylni matnga aylantirishda muammo yuzaga keldi. Iltimos matnli xabar yuboring."


    def add_chiqimlar(self, text):
        add_chiqim = {
                "name": "add_chiqim_f",
                "description": "chiqimlarni saqlash uchun",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "summa": {
                            "type": "INTEGER",
                            "description": "chiqimning summasi, qancha ekani, masalan: 90000 so'm, 180000 so'm",
                        },
                        "kategoriya": {
                            "type": "STRING",
                            "enum": ["ovqat", "kiyim", "mashina", "ta'lim"],
                            "description": "chiqimning kategoriyasi, nima maqsadda sarf qilingani ",
                        },
                        "izoh": {
                            "type": "STRING",
                            "description": "bu qo'shimcha, bu shunchaki harajat uchun qandaydir izoh",
                        },
                    },
                    "required": ["summa", "kategoriya", "izoh"],
                },
            }
        tools = types.Tool(function_declarations=[add_chiqim]) # type: ignore
        
        print("salom")


        contents = [
            types.Content(
                role="user", parts=[types.Part(text=text)]
            )
        ]
        config = types.GenerateContentConfig(tools=[tools])


        # Send request with function declarations
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=config,
        )
        
        # Check if response has candidates and function call
        if (response.candidates and 
            len(response.candidates) > 0 and 
            response.candidates[0].content and 
            response.candidates[0].content.parts and 
            len(response.candidates[0].content.parts) > 0):
            
            tool_call = response.candidates[0].content.parts[0].function_call
            
            if tool_call and hasattr(tool_call, 'name') and tool_call.name == "add_chiqim_f":
                result = self.add_chiqim_f(**tool_call.args)
                print(f"Function execution result: {result}")
            else:
                print("No function call made or function name doesn't match")
        else:
            print("No valid response received from Gemini")

    def process_text_message(self, text, user_id: int = 23, user_name: str = "Foydalanuvchi"):
        """
        Process text message to determine if it's income or expense and add to database
        
        Args:
            text: The text message from user
            user_id: User ID for database operations
            user_name: User name for report formatting
            
        Returns:
            Result message for user
        """
        # Create function declarations for both income and expense
        add_chiqim = {
            "name": "add_chiqim_f",
            "description": "chiqimlarni (harajat) saqlash uchun",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "summa": {
                        "type": "INTEGER",
                        "description": "chiqimning summasi, qancha ekani, masalan: 90000 so'm, 180000 so'm",
                    },
                    "kategoriya": {
                        "type": "STRING",
                        "enum": ["ovqat", "kiyim", "mashina", "ta'lim", "transport", "sog'liq", "boshqa"],
                        "description": "chiqimning kategoriyasi, nima maqsadda sarf qilingani",
                    },
                    "izoh": {
                        "type": "STRING",
                        "description": "bu qo'shimcha, bu shunchaki harajat uchun qandaydir izoh",
                    },
                },
                "required": ["summa", "kategoriya", "izoh"],
            },
        }
        
        add_kirim = {
            "name": "add_kirim_f",
            "description": "kirimlarni (daromad) saqlash uchun",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "summa": {
                        "type": "INTEGER",
                        "description": "kirimning summasi, qancha ekani, masalan: 500000 so'm, 1000000 so'm",
                    },
                    "kategoriya": {
                        "type": "STRING",
                        "enum": ["ish haqi", "biznes", "savdo", "investitsiya", "grant", "boshqa"],
                        "description": "kirimning kategoriyasi, qayerdan kelgan daromad",
                    },
                    "izoh": {
                        "type": "STRING",
                        "description": "bu qo'shimcha, bu shunchaki daromad uchun qandaydir izoh",
                    },
                },
                "required": ["summa", "kategoriya", "izoh"],
            },
        }
        
        tools = types.Tool(function_declarations=[add_chiqim, add_kirim])
        
        contents = [
            types.Content(
                role="user", 
                parts=[types.Part(text=f"Ushbu matnni tahlil qiling va agar bu harajat (chiqim) yoki daromad (kirim) haqida bo'lsa, tegishli funksiyalarni chaqiring. Agar bir xabarda ikkala operatsiya ham bo'lsa, ikkalasini ham alohida chaqiring. Matn: {text}")]
            )
        ]
        config = types.GenerateContentConfig(tools=[tools])

        try:
            # Send request with function declarations
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents,
                config=config,
            )
            
            # Check if response has candidates and function calls
            if (response.candidates and 
                len(response.candidates) > 0 and 
                response.candidates[0].content and 
                response.candidates[0].content.parts and 
                len(response.candidates[0].content.parts) > 0):
                
                # Process all function calls (can be multiple)
                results = []
                function_calls_made = False
                
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        tool_call = part.function_call
                        function_calls_made = True
                        
                        if tool_call.name == "add_chiqim_f":
                            result = self.add_chiqim_f(**tool_call.args, user_id=user_id)
                            # Get the latest added record
                            latest_record = db.get_latest_chiqim(user_id)
                            if latest_record:
                                results.append(self.format_report_message("chiqim", latest_record, user_name))
                            else:
                                results.append(f"✅ Harajat qo'shildi: {tool_call.args.get('summa', 'N/A')} so'm - {tool_call.args.get('kategoriya', 'N/A')}")
                                
                        elif tool_call.name == "add_kirim_f":
                            result = self.add_kirim_f(**tool_call.args, user_id=user_id)
                            # Get the latest added record
                            latest_record = db.get_latest_kirim(user_id)
                            if latest_record:
                                results.append(self.format_report_message("kirim", latest_record, user_name))
                            else:
                                results.append(f"✅ Daromad qo'shildi: {tool_call.args.get('summa', 'N/A')} so'm - {tool_call.args.get('kategoriya', 'N/A')}")
                        else:
                            results.append("❌ Xato: Noma'lum funksiya chaqirildi")
                
                if function_calls_made:
                    # Combine all results
                    if len(results) > 1:
                        return "\n\n" + "="*50 + "\n\n".join(results)
                    else:
                        return results[0] if results else "❌ Xato: Hech qanday operatsiya amalga oshirilmadi"
                else:
                    return """❌ Ushbu xabar harajat yoki daromad haqida emas.

📝 To'g'ri formatda yozing:
• "Ovqat uchun 50000 so'm sarf qildim"
• "Ish haqim 2000000 so'm oldim" 
• "Transport uchun 15000 so'm to'ladim"
• "Bugun ovqat uchun 50000 so'm sarf qildim va ish haqim 2000000 so'm oldim"

💡 Maslahat: Summa, kategoriya va maqsadni aniq yozing."""
            else:
                return """❌ AI javob bermadi. 

🔄 Qayta urinib ko'ring yoki:
• Xabarni qayta yozing
• Summa va kategoriyani aniq belgilang
• Internet aloqasini tekshiring"""
                
        except Exception as e:
            print(f"Error in process_text_message: {e}")
            error_str = str(e)
            
            # Check for specific error types
            if "FAILED_PRECONDITION" in error_str and "location is not supported" in error_str:
                return """❌ Xato: Google AI xizmati sizning mintaqangizda ishlamaydi.

🔧 Yechimlar:
• VPN ishlatib qayta urinib ko'ring
• Matnli xabar yuboring (audio o'rniga)
• Administrator bilan bog'laning

📝 Matnli format:
• "Ovqat uchun 50000 so'm sarf qildim"
• "Ish haqim 2000000 so'm oldim"
• "Transport uchun 15000 so'm to'ladim" """
            elif "400" in error_str:
                return "❌ Xato: API so'rovida xatolik. Iltimos qayta urinib ko'ring."
            elif "403" in error_str:
                return "❌ Xato: API kaliti noto'g'ri yoki cheklangan. Administrator bilan bog'laning."
            elif "429" in error_str:
                return "❌ Xato: API limiti tugagan. Iltimos biroz kutib qayta urinib ko'ring."
            else:
                return f"❌ Xato: {str(e)}"

    def format_report_message(self, record_type: str, record_data: tuple, user_name: str = "Foydalanuvchi"):
        """
        Format a report message for income or expense records
        
        Args:
            record_type: "kirim" or "chiqim"
            record_data: Database record tuple (id, summa, izoh, kategoriya, user_id)
            user_name: User's name
            
        Returns:
            Formatted report message
        """
        try:
            if not record_data:
                return "❌ Ma'lumot topilmadi"
            
            # Extract data from tuple
            record_id, summa, izoh, kategoriya, user_id = record_data
            
            # Get current date
            from datetime import datetime
            current_date = datetime.now().strftime("%d/%m/%Y %I:%M %p")
            
            # Format the message
            if record_type == "kirim":
                type_text = "Kirim (Daromad)"
                emoji = "💰"
            else:
                type_text = "Chiqim (Harajat)"
                emoji = "💸"
            
            message = f"""Hisobotga qo'shildi ✅

{emoji} {type_text}
👤 Foydalanuvchi: {user_name}
📅 Sana: {current_date}

💵 Summa: {summa} so'm
📂 Kategoriya: {kategoriya}
📝 Izoh: {izoh}"""
            
            return message
            
        except Exception as e:
            print(f"Error formatting report message: {e}")
            return f"❌ Xato: {str(e)}"
