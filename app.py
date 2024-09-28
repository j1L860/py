from flask import Flask, request, render_template
import pandas as pd
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure the upload folder exists
if not os.path.exists('uploads'):
    os.makedirs('uploads')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    file1 = request.files['file1']
    file2 = request.files['file2']
    
    filepath1 = os.path.join(app.config['UPLOAD_FOLDER'], 'FileS.txt')
    filepath2 = os.path.join(app.config['UPLOAD_FOLDER'], 'File3_2.txt')
    
    file1.save(filepath1)
    file2.save(filepath2)
    
    sample_data = pd.read_csv(filepath1)
    reference_data = pd.read_csv(filepath2)

    results = []
    for index, row in sample_data.iterrows():
        position = row['POSITION']
        result = row['RESULT']
        second_nucleotide = result[1] if len(result) > 1 else result
        
        ref_row = reference_data[reference_data['POSITION'] == position]
        if not ref_row.empty:
            ref_allele = ref_row['RESULT'].values[0]
            match_status = 'positive' if second_nucleotide in ref_allele else 'negative'
            haplogroup = ref_row['HAPLOGROUP'].values[0]
            results.append((position, match_status, haplogroup))
    
    results_df = pd.DataFrame(results, columns=['POSITION', 'STATUS', 'HAPLOGROUP'])
    positive_snps_count = results_df[results_df['STATUS'] == 'positive'].shape[0]

    haplogroup_status = results_df.groupby(['HAPLOGROUP', 'STATUS']).size().unstack(fill_value=0)
    plt.figure(figsize=(10, 6))
    haplogroup_status.plot(kind='bar', stacked=True, color=['red', 'green'])
    plt.xlabel('Haplogroup')
    plt.ylabel('Number of SNPs')
    plt.title('Haplogroup Confirmation Results')
    
    plot_path = os.path.join(app.config['UPLOAD_FOLDER'], 'result_plot.png')
    plt.savefig(plot_path)
    plt.close()

    return render_template('index.html', positive_snps_count=positive_snps_count, plot_url=plot_path)

if __name__ == '__main__':
    app.run()