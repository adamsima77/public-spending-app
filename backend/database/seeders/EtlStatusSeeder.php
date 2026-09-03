<?php

namespace Database\Seeders;

use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use App\Models\EtlStatus;

class EtlStatusSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        $statuses = ['pending', 'downloading', 'downloaded', 'failed', 'parsed'];
        
        foreach ($statuses as $name) {
            EtlStatus::updateOrInsert(['name' => $name]);
        }
    }
}