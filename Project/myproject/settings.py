DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'Tour operator',
        'USER': '',
        'PASSWORD': '',
        'HOST': 'DESKTOP-PD6GE3V\\SQLEXPRESS',  # ← ชื่อเครื่องใหม่!
        'PORT': '',
        'OPTIONS': {
            'driver': 'ODBC Driver 18 for SQL Server',
            'extra_params': 'TrustServerCertificate=yes',
        },
    }
}