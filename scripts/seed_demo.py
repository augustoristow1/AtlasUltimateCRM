"""
Demo data seed script.
Run: python scripts/seed_demo.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from atlas_ultimate_crm.bootstrap import Bootstrap


def seed():
    print("Seeding demo data...")
    bs = Bootstrap()
    bs.initialize()
    ws = bs.workspace_id

    # Contacts
    contacts_data = [
        ("Carlos Mendes", "+5511991111111", "carlos@empresa.com", "São Paulo"),
        ("Fernanda Lima", "+5511992222222", "fernanda@negocio.com", "Campinas"),
        ("Roberto Alves", "+5511993333333", "roberto@tech.com", "Rio de Janeiro"),
        ("Ana Beatriz", "+5511994444444", "ana@startup.io", "Belo Horizonte"),
        ("Marcos Souza", "+5511995555555", "marcos@corp.com.br", "Curitiba"),
    ]
    contacts = []
    for name, phone, email, city in contacts_data:
        c = bs.contact_service.create_contact(ws, name, phone=phone, email=email, city=city)
        contacts.append(c)
        print(f"  Contact: {c.name}")

    # Companies
    companies_data = [
        ("TechNova Soluções", "Tecnologia", "São Paulo"),
        ("Meridian Saúde", "Saúde", "Campinas"),
        ("Global Trade BR", "Comércio", "Rio de Janeiro"),
    ]
    companies = []
    for name, industry, city in companies_data:
        c = bs.company_service.create_company(ws, name, industry=industry, city=city)
        companies.append(c)
        print(f"  Company: {c.name}")

    # Pipeline & Deals
    pipeline, stages = bs.pipeline_service.get_or_create_default_pipeline(ws)
    deals_data = [
        ("Licença Enterprise TechNova", contacts[0].id, 48000.0, stages[2].id),
        ("Projeto Meridian Phase 2", contacts[1].id, 32000.0, stages[3].id),
        ("Global Trade Integração", contacts[2].id, 15000.0, stages[1].id),
    ]
    for title, contact_id, value, stage_id in deals_data:
        d = bs.deal_service.create_deal(ws, pipeline.id, stage_id, title, contact_id=contact_id, value=value)
        print(f"  Deal: {d.title}")

    # Tasks
    from datetime import datetime, UTC, timedelta
    tasks_data = [
        ("Ligar para Carlos sobre proposta", contacts[0].id),
        ("Enviar contrato para Fernanda", contacts[1].id),
        ("Agendar demo para Roberto", contacts[2].id),
    ]
    for title, contact_id in tasks_data:
        t = bs.task_service.create_task(ws, title, contact_id=contact_id, due_at=datetime.now(UTC) + timedelta(days=2))
        print(f"  Task: {t.title}")

    # Conversations & Messages
    for contact in contacts[:3]:
        conv = bs.conversation_service.get_or_create_conversation(ws, contact.id)
        bs.messaging_service.send_text_to_contact(ws, contact.id, contact.phone, f"Olá {contact.name}, tudo bem?")
        bs.messaging_service.handle_inbound(ws, contact.id, contact.phone, "Tudo ótimo! E você?", provider_message_id=f"seed_{contact.id[:8]}")
        print(f"  Conversation: {contact.name}")

    # Campaign
    campaign = bs.campaign_service.create_campaign(ws, "Campanha Boas-Vindas Q4")
    bs.campaign_service.add_recipients(campaign.id, [c.id for c in contacts])
    bs.campaign_service.run_campaign(campaign.id, ws)
    print(f"  Campaign: {campaign.name}")

    print("\nSeed complete!")
    print(f"Workspace: {ws}")
    print(f"Contacts: {len(contacts)}")
    print(f"Companies: {len(companies)}")


if __name__ == "__main__":
    seed()
