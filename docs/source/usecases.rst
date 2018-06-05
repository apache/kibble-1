Use Cases
========================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

**********************
Add an Organisation
**********************
This use case describes the process of adding an organisation

Actors: 
      User

Precondition: 
      User is logged in

Flow of Events:
      1. The use case starts when the user is on the Organisation tab.
      2. The system loads any previously created organisations and the form to create a new organisation
      3. The user can enter an organisation name, description, and ID.
      4. The system will verify the information.
      5. The system will add the new organisation.
      6. The system will then display the new organisation along with any existing organisations.
      
Exception Scenario:
      The user does not enter an organisation name or description.

Post Conditions: 
      The user creates the organisation or leaves the page.


**********************
Add a View
**********************
This use case describes the process of adding a view to an organisation

Actors: 
      User

Precondition: 
      User is logged in and has an organisation created

Flow of Events:
      1. The use case starts when the user is on the Views tab.
      2. The user will click on the "Create a new view" button.
      3. The system loads the form to create a new view.
      4. The user will information needed to create the view.
      5. The system will verify the information.
      6. The system will add the new view.
      7. The system will then display the new view along with any existing views.
      8. The user with then be able to edit or delete the view.
      
Exception Scenario:
      The user does not enter a view name.

Post Conditions: 
      The user creates the source or leaves the page.
      

**********************
Add a Source
**********************
This use case describes the process of adding a source to an organisation

Actors: 
      User

Precondition: 
      User is logged in and has an organisation created

Flow of Events:
      1. The use case starts when the user is on the Sources tab.
      2. The system loads any existing sources and the form to create a new source.
      3. The user will select a source type from the list provided.
      4. The user will enter a source URL/ID and a username and password if needed.
      5. The system will verify the information.
      6. The system will add the new source.
      7. The system will then display the new source along with any existing sources.
      8. The user with then have to run the kibble scanner to process the new source.
      
Exception Scenario:
      The user does not enter a source URL/ID.

Post Conditions: 
      The user creates the source or leaves the page.
            

**********************
Add a User
**********************
This use case describes the process of adding a user to an organisation

Actors: 
      User

Precondition: 
      User is logged in and has an organisation created

Flow of Events:
      1. The use case starts when the user is on the Users tab.
      2. The system loads the form to invite a new member and the current membership of the organisation.
      3. The user will enter the email address of a user.
      4. The system will verify the information.
      5. The system will add the user to the organisation's membership.
      
Exception Scenario:
      The user enters a user that does not exist.

Post Conditions: 
      The user invites a member or leaves the page.
            
      
