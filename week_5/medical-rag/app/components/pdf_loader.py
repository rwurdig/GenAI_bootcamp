import os
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.common.logger import get_logger
from app.common.custom_exception import CustomException
from app.config.config import DATA_PATH, CHUNK_SIZE, CHUNK_OVERLAP

logger = get_logger(__name__)

def load_pdf_files():
    try:
        if not os.path.exists(DATA_PATH):
            # Create sample medical data if no PDFs exist
            logger.info("No PDF files found, creating sample medical data...")
            return create_sample_medical_docs()
        
        logger.info(f"Loading files from {DATA_PATH}")

        loader = DirectoryLoader(DATA_PATH, glob="*.pdf", loader_cls=PyPDFLoader)
        documents = loader.load()

        if not documents:
            logger.warning("No PDFs were found, using sample data")
            return create_sample_medical_docs()
        else:
            logger.info(f"Successfully fetched {len(documents)} documents")

        return documents
    
    except Exception as e:
        error_message = CustomException("Failed to load PDF", e)
        logger.error(str(error_message))
        return create_sample_medical_docs()


def create_sample_medical_docs():
    """Create sample medical documents for demo purposes"""
    from langchain_core.documents import Document
    
    medical_info = [
        {
            "content": """Influenza (Flu) - Complete Guide:
            
The flu is a contagious respiratory illness caused by influenza viruses. It is different from the common cold and can cause mild to severe illness.

SYMPTOMS OF THE FLU:
- Fever (100°F or higher) or feeling feverish/chills
- Cough (usually dry)
- Sore throat
- Runny or stuffy nose
- Muscle or body aches
- Headaches
- Fatigue and weakness
- Some people may have vomiting and diarrhea (more common in children)

HOW TO RECOVER FROM THE FLU:
1. REST: Stay home and get plenty of sleep. Your body needs energy to fight the infection.
2. HYDRATION: Drink plenty of fluids - water, clear broths, sports drinks, herbal teas. Avoid alcohol and caffeine.
3. MEDICATIONS:
   - Antivirals (Tamiflu/oseltamivir, Relenza/zanamivir) - Most effective if started within 48 hours of symptoms
   - Fever reducers: Acetaminophen (Tylenol) or Ibuprofen (Advil)
   - Decongestants for nasal congestion
   - Cough suppressants if needed
4. HOME REMEDIES:
   - Warm liquids (chicken soup, tea with honey)
   - Use a humidifier
   - Gargle with salt water for sore throat
   - Steam inhalation for congestion
5. RECOVERY TIME: Most people recover within 1-2 weeks. Fatigue may last longer.

WHEN TO SEEK EMERGENCY CARE:
- Difficulty breathing or shortness of breath
- Persistent chest pain or pressure
- Confusion or altered mental state
- Severe or persistent vomiting
- Flu symptoms that improve then return with fever and worse cough

PREVENTION:
- Annual flu vaccination (best protection)
- Wash hands frequently
- Avoid close contact with sick people
- Cover coughs and sneezes
- Clean and disinfect surfaces""",
            "metadata": {"source": "medical_guide", "topic": "influenza_flu"}
        },
        {
            "content": """Common Cold vs. Flu - Know the Difference:

COMMON COLD:
- Gradual onset of symptoms
- Mild fever (rare in adults)
- Runny/stuffy nose (prominent)
- Sneezing (common)
- Mild body aches
- Mild fatigue
- Usually lasts 7-10 days

INFLUENZA (FLU):
- Sudden onset of symptoms
- High fever (102-104°F), chills
- Headache (prominent)
- Severe body aches
- Extreme fatigue
- Dry cough
- Usually lasts 1-2 weeks

TREATMENT FOR COMMON COLD:
- Rest and hydration
- Over-the-counter pain relievers
- Decongestants
- Honey for cough (adults)
- Warm liquids

TREATMENT FOR FLU:
- All of the above PLUS:
- Antiviral medications (if caught early)
- More rest required
- Monitor for complications
- May need medical attention""",
            "metadata": {"source": "medical_guide", "topic": "cold_vs_flu"}
        },
        {
            "content": """Diabetes Management Guidelines:
            
Diabetes is a chronic condition affecting how your body processes blood sugar (glucose).

TYPE 1 DIABETES: Autoimmune condition where the body doesn't produce insulin.
TYPE 2 DIABETES: Body doesn't use insulin properly (insulin resistance).

DAILY MANAGEMENT:
- Monitor blood sugar levels regularly
- Take medications as prescribed
- Follow a balanced diet
- Exercise regularly (150 minutes/week)
- Maintain healthy weight

TARGET BLOOD SUGAR LEVELS:
- Fasting: 80-130 mg/dL
- 2 hours after meals: Less than 180 mg/dL
- A1C: Less than 7%

WARNING SIGNS - HIGH BLOOD SUGAR:
- Frequent urination
- Excessive thirst
- Blurred vision
- Fatigue
- Slow-healing wounds

WARNING SIGNS - LOW BLOOD SUGAR:
- Shakiness
- Sweating
- Confusion
- Rapid heartbeat
- Hunger

DIET RECOMMENDATIONS:
- Limit refined carbohydrates and sugars
- Choose whole grains
- Eat plenty of vegetables
- Include lean proteins
- Monitor portion sizes""",
            "metadata": {"source": "medical_guide", "topic": "diabetes"}
        },
        {
            "content": """Hypertension (High Blood Pressure):

Blood pressure is measured as systolic/diastolic (e.g., 120/80 mmHg).

BLOOD PRESSURE CATEGORIES:
- Normal: Less than 120/80 mmHg
- Elevated: 120-129 / less than 80 mmHg
- Stage 1 Hypertension: 130-139 / 80-89 mmHg
- Stage 2 Hypertension: 140+ / 90+ mmHg
- Hypertensive Crisis: Higher than 180/120 mmHg (seek emergency care)

LIFESTYLE CHANGES TO LOWER BLOOD PRESSURE:
1. DASH Diet (Dietary Approaches to Stop Hypertension)
2. Reduce sodium (less than 2,300 mg daily, ideally 1,500 mg)
3. Exercise regularly (30 minutes most days)
4. Maintain healthy weight
5. Limit alcohol
6. Quit smoking
7. Manage stress
8. Get adequate sleep

MEDICATIONS:
- ACE inhibitors (lisinopril, enalapril)
- Beta-blockers (metoprolol, atenolol)
- Calcium channel blockers (amlodipine)
- Diuretics (hydrochlorothiazide)

MONITORING:
- Check blood pressure regularly
- Keep a log for your doctor
- Take medications as prescribed""",
            "metadata": {"source": "medical_guide", "topic": "hypertension"}
        },
        {
            "content": """Headache Types and Treatment:

TENSION HEADACHES (Most Common):
- Symptoms: Dull, aching pain on both sides, tight band feeling
- Treatment: OTC pain relievers (ibuprofen, acetaminophen), stress management, adequate sleep, massage

MIGRAINE:
- Symptoms: Throbbing pain (usually one side), nausea, sensitivity to light/sound, may have aura
- Treatment: Prescription triptans, rest in dark quiet room, cold compress, preventive medications

CLUSTER HEADACHES:
- Symptoms: Severe pain around one eye, tearing, nasal congestion
- Treatment: Oxygen therapy, prescription medications, preventive treatments

SINUS HEADACHES:
- Symptoms: Pain in forehead, cheeks, bridge of nose, worse when bending
- Treatment: Decongestants, nasal irrigation, treat underlying infection

SEEK EMERGENCY CARE IF:
- Sudden, severe "thunderclap" headache
- Headache with fever, stiff neck, confusion
- Headache after head injury
- Headache with vision changes, weakness, or speech problems
- Worst headache of your life""",
            "metadata": {"source": "medical_guide", "topic": "headaches"}
        },
        {
            "content": """First Aid Essentials:

MINOR CUTS AND SCRAPES:
1. Wash hands before treating
2. Stop bleeding with gentle pressure
3. Clean wound with water
4. Apply antibiotic ointment
5. Cover with sterile bandage
6. Watch for signs of infection

BURNS:
- First-Degree: Cool water 10-20 min, aloe vera, OTC pain relief
- Second-Degree: Cool water, don't pop blisters, sterile bandage, seek medical care for large burns
- Third-Degree: Call 911, don't remove clothing stuck to burn, cover with clean cloth

SPRAINS:
- R.I.C.E: Rest, Ice, Compression, Elevation
- OTC pain relievers
- Seek care if you can't bear weight or severe swelling

FEVER MANAGEMENT:
- Adults: Take acetaminophen or ibuprofen
- Stay hydrated
- Rest
- Seek care if fever is 103°F+ or lasts more than 3 days

WHEN TO CALL 911:
- Difficulty breathing
- Chest pain
- Signs of stroke (FAST: Face drooping, Arm weakness, Speech difficulty, Time to call)
- Severe bleeding
- Loss of consciousness
- Severe allergic reaction""",
            "metadata": {"source": "medical_guide", "topic": "first_aid"}
        }
    ]
    
    documents = [
        Document(page_content=item["content"], metadata=item["metadata"])
        for item in medical_info
    ]
    
    logger.info(f"Created {len(documents)} sample medical documents")
    return documents


def create_text_chunks(documents):
    try:
        if not documents:
            raise CustomException("No documents were found")
        
        logger.info(f"Splitting {len(documents)} documents into chunks")

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE, 
            chunk_overlap=CHUNK_OVERLAP
        )

        text_chunks = text_splitter.split_documents(documents)

        logger.info(f"Generated {len(text_chunks)} text chunks")
        return text_chunks
    
    except Exception as e:
        error_message = CustomException("Failed to generate chunks", e)
        logger.error(str(error_message))
        return []
