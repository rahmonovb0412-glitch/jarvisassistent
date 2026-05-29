' ════════════════════════════════════════════════
'  Jarvis - Terminalsiz ishga tushirish (Windows)
'  Bu faylga 2 marta bossangiz, qora terminal
'  ko'rinmaydi - faqat Jarvis oynasi ochiladi.
' ════════════════════════════════════════════════
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Skript joylashgan papka
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
shell.CurrentDirectory = scriptDir

' pythonw bilan ishga tushirish (terminal ko'rinmaydi)
' 0 = oyna yashirin, False = kutmasdan davom etish
shell.Run "pythonw app.py", 0, False
