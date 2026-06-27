'''
Important functions that I don't know where they go.
'''

#-------------------------------------------------------------------------------------------------------
# Context processor injects restaurant_settings into every template automatically
#-------------------------------------------------------------------------------------------------------
@app.context_processor
def inject_settings():
    try:
        settings = RestaurantSettings.query.first()
    except Exception:
        settings = None
    return dict(restaurant_settings=settings)

