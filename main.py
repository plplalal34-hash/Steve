@client.event
async def on_message(message):
    if message.author == client.user: return

    async with message.channel.typing():
        try:
            response = model.generate_content(message.content)
            # التأكد من أن الرد يحتوي على نص
            if response and response.candidates[0].content.parts:
                await message.channel.send(response.text[:2000])
            else:
                await message.channel.send("⚠️ تم حجب الرد بواسطة فلاتر الأمان من جوجل.")
        except Exception as e:
            error_msg = str(e)
            print(f"Error: {error_msg}")
            
            # سيخبرك البوت هنا بالخطأ الحقيقي في الشات
            if "API_KEY_INVALID" in error_msg:
                await message.channel.send("❌ خطأ: مفتاح الـ API غير صحيح أو لم يتم تفعيله بعد.")
            elif "quota" in error_msg.lower():
                await message.channel.send("⏳ خطأ: انتهت حدود الاستخدام المجانية لهذا اليوم.")
            elif "404" in error_msg:
                await message.channel.send("❌ خطأ: الموديل 1.5 Flash غير متاح في منطقتك أو حسابك.")
            else:
                await message.channel.send(f"⚙️ خطأ تقني داخلي: `{error_msg[:100]}`")
                
