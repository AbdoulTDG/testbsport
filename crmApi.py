# Bibliothèques
from hubspot.crm.contacts import SimplePublicObjectInput
from hubspot.crm.contacts.exceptions import ApiException
from hubspot import HubSpot

class CrmApi( ):
        
    
    
    
    def __init__(self,token) -> None:
        # Connection à l'API
        self.token=token
        self.api_client = HubSpot(access_token=self.token)

    # Récupération du montant total des deals sans pondération
    def total_deal_value(self):
        
        # Recupération des ids des deals (si on considère que tous les deals sont associés à une seule entreprise)
        self.deals_id=[]
        self.deals=self.api_client.crm.deals.get_all()
        for deal in self.deals:
            self.deals_id.append(deal.to_dict()["id"])

        self.montant_deals=0
        for id in self.deals_id:
            self.deal_data=self.api_client.crm.deals.basic_api.get_by_id(id,properties=["amount"]).to_dict()
            self.montant_deals+=float(self.deal_data["properties"]["amount"])
        return self.montant_deals


    # Calcul du montant total des deals avec pondération
    def total_deal_value_weighted(self):
        # Recupération des ids des deals (si on considère que tous les deals sont associés à une seule entreprise)
        self.deals_id=[]
        self.deals=self.api_client.crm.deals.get_all()
        for deal in self.deals:
            self.deals_id.append(deal.to_dict()["id"])
        
        # Calcul du montant total des deals avec pondération
        self.montant_deals_pond=0
        for id in self.deals_id:
            self.deal_data=self.api_client.crm.deals.basic_api.get_by_id(id,properties=["amount","hs_deal_stage_probability"]).to_dict()
            self.montant_deals_pond+=float(self.deal_data["properties"]["amount"]) * float(self.deal_data["properties"]["hs_deal_stage_probability"])
        return self.montant_deals_pond

    # Update d'un deal
    def update_deal(self,deal_id,amount):
        try:
            self.update_montant_deal = SimplePublicObjectInput(
                        properties={"amount":amount})
            self.api_client.crm.deals.basic_api.update(simple_public_object_input=self.update_montant_deal,deal_id=deal_id)
            return print(f"Deal {deal_id} updated")
        except ApiException as deal:
            return print("Exception when updatin deal: %s\n" %deal)  
        

    # Calcul du nombre de contacts dont En poste = Oui
    def count_en_poste(self,etat="Oui"):

        # Récupération des id des contacts
        self.contacts_id=[]
        self.contacts=self.api_client.crm.contacts.get_all()
        for contact in self.contacts:
            self.contacts_id.append(contact.to_dict()["id"])

        # Calcul du nombre de contact selon l'état de l'attribut en poste
        cpt_en_poste=0
        for id in self.contacts_id:
            self.contact_data=self.api_client.crm.contacts.basic_api.get_by_id(id,properties=["en_poste"]).to_dict()
            if self.contact_data["properties"]["en_poste"] == etat:
                cpt_en_poste+=1
        return cpt_en_poste

    # Propriétaire actuel
    def update_owner(self):
        self.owner_id=self.api_client.crm.companies.basic_api.get_by_id(7496989169,properties=["hubspot_owner_id"]).to_dict()
        self.owner_id=self.owner_id["properties"]["hubspot_owner_id"]
        self.owner_data=self.api_client.crm.owners.owners_api.get_by_id(self.owner_id).to_dict()
        return [self.owner_data["first_name"],self.owner_data["last_name"]]

    # Mise à jour des infos de l'entreprise
    def update_company(self,comp_id="7496989169"):
            try:
                    self.update_montant_tot_deals = SimplePublicObjectInput(properties={
                    "valeur_totale_des_deals":self.total_deal_value() ,
                    "valeur_totale_des_deals_ponderee":self.total_deal_value_weighted(),
                    "nombre_de_points_de_contacts_en_poste": self.count_en_poste(),
                    "nom_du_dirigeant":self.update_owner()[1],
                    "prenom_du_dirigeant":self.update_owner()[0]})
                    self.api_client.crm.companies.basic_api.update(simple_public_object_input=self.update_montant_tot_deals,company_id=comp_id)
                    return print("company updated")
            except ApiException as update:
                    return print("Exception when updating company: %s\n" % update)
    


    # Récupération des infos de l'entreprise
    def comp_info(self,comp_id="7496989169"):
        self.company_data=self.api_client.crm.companies.basic_api.get_by_id(comp_id,properties=["name","city","country","industry",
                                                                                "nom_du_dirigeant","prenom_du_dirigeant",
                                                                                "numberofemployees","valeur_totale_des_deals",
                                                                                "valeur_totale_des_deals_ponderee","num_associated_deals",
                                                                                "nombre_de_points_de_contacts_en_poste",
                                                                                "nombre_de_points_de_contacts_en_poste"]).to_dict()
        return self.company_data["properties"]