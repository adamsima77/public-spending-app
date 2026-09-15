<?php

namespace Database\Seeders;

use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use App\Models\NutCode;

class NutCodeSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        $codes = [
            ['code' => 'SK',    'name_sk' => 'Slovensko',              'level' => 0, 'parent_code' => null],
            ['code' => 'SK0',   'name_sk' => 'Slovensko',              'level' => 1, 'parent_code' => 'SK'],
            ['code' => 'SK01',  'name_sk' => 'Bratislavský kraj',      'level' => 2, 'parent_code' => 'SK0'],
            ['code' => 'SK010', 'name_sk' => 'Bratislavský kraj',      'level' => 3, 'parent_code' => 'SK01'],
            ['code' => 'SK02',  'name_sk' => 'Západné Slovensko',      'level' => 2, 'parent_code' => 'SK0'],
            ['code' => 'SK021', 'name_sk' => 'Trnavský kraj',          'level' => 3, 'parent_code' => 'SK02'],
            ['code' => 'SK022', 'name_sk' => 'Trenčiansky kraj',       'level' => 3, 'parent_code' => 'SK02'],
            ['code' => 'SK023', 'name_sk' => 'Nitriansky kraj',        'level' => 3, 'parent_code' => 'SK02'],
            ['code' => 'SK03',  'name_sk' => 'Stredné Slovensko',      'level' => 2, 'parent_code' => 'SK0'],
            ['code' => 'SK031', 'name_sk' => 'Žilinský kraj',          'level' => 3, 'parent_code' => 'SK03'],
            ['code' => 'SK032', 'name_sk' => 'Banskobystrický kraj',   'level' => 3, 'parent_code' => 'SK03'],
            ['code' => 'SK04',  'name_sk' => 'Východné Slovensko',     'level' => 2, 'parent_code' => 'SK0'],
            ['code' => 'SK041', 'name_sk' => 'Prešovský kraj',         'level' => 3, 'parent_code' => 'SK04'],
            ['code' => 'SK042', 'name_sk' => 'Košický kraj',           'level' => 3, 'parent_code' => 'SK04'],
       ];

       foreach ($codes as $code) {
           NutCode::create($code);
       }
    }
}
