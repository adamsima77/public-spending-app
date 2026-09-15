<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;
use Illuminate\Support\Facades\DB;
use XMLReader;

class ImportCpvCodes extends Command
{
    protected $signature = 'import:cpv-codes';
    protected $description = 'Naimportuje CPV číselník zo statického resources/data/cpv.gc súboru';

    public function handle(): int
    {
        $path = resource_path('data/cpv.gc');

        if (!file_exists($path)) {
            $this->error("Súbor nenájdený: {$path}. Stiahni ho z https://raw.githubusercontent.com/OP-TED/eForms-SDK/main/codelists/cpv.gc");
            return self::FAILURE;
        }

        $this->info('Parsujem cpv.gc');

        $reader = new XMLReader();
        $reader->open($path);

        $rows = [];
        $count = 0;

        while ($reader->read()) {
            if ($reader->nodeType === XMLReader::ELEMENT && $reader->localName === 'Row') {
                $rowXml = $reader->readOuterXml();
                $row = $this->parseRow($rowXml);

                if ($row !== null) {
                    $rows[] = $row;
                    $count++;
                }

                if (count($rows) >= 500) {
                    $this->upsertRows($rows);
                    $rows = [];
                }

                $reader->next();
            }
        }

        if (count($rows) > 0) {
            $this->upsertRows($rows);
        }

        $reader->close();
        $this->info("Hotovo. Naimportovaných {$count} CPV kódov.");
        return self::SUCCESS;
    }

    private function parseRow(string $rowXml): ?array
    {
        $xml = simplexml_load_string(
            '<Row xmlns="http://docs.oasis-open.org/codelist/ns/genericode/1.0/">' . substr($rowXml, 5)
        );

        if ($xml === false) {
            return null;
        }

        $values = [];
        foreach ($xml->Value as $value) {
            $columnRef = (string) $value['ColumnRef'];
            $values[$columnRef] = (string) $value->SimpleValue;
        }

        $rawCode = $values['code'] ?? null;
        if (! $rawCode) {
            return null;
        }

        $code = explode('-', $rawCode)[0];
        $parentRaw = $values['parentCode'] ?? null;
        $parentCode = $parentRaw ? explode('-', $parentRaw)[0] : null;

        return [
            'code' => $code,
            'name_sk' => $values['slk_label'] ?? $values['eng_label'] ?? null,
            'level' => $this->deriveLevel($code),
            'parent_code' => $parentCode,
            'created_at' => now(),
            'updated_at' => now(),
        ];
    }

    private function upsertRows(array $rows): void
    {
        DB::table('cpv_codes')->upsert($rows, ['code'], ['name_sk', 'level', 'parent_code', 'updated_at']);
    }

    private function deriveLevel(string $code): int
    {
        $clean = rtrim($code, '0');
        $length = strlen($clean);
        return $length <= 2 ? 1 : $length - 1;
    }
}