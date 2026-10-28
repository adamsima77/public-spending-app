<?php

declare(strict_types=1);

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;
use RuntimeException;

class EformsCodelistSeeder extends Seeder
{
    public function run(): void
    {
        $contents = file_get_contents(database_path('data/eforms_codelists.json'));

        if ($contents === false) {
            throw new RuntimeException('Unable to read the eForms codelists data file.');
        }

        $data = json_decode(
            $contents,
            true,
            512,
            JSON_THROW_ON_ERROR,
        );

        DB::transaction(function () use ($data): void {
            foreach ($data['lists'] as $table => $list) {
                if (empty($list['rows'])) {
                    continue;
                }

                DB::table($table)->upsert($list['rows'], ['code'], ['label_sk']);
            }
        });
    }
}
